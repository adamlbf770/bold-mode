#!/usr/bin/env python3
"""bold-mode guard: enforces the step budget and the blast radius during a bold run.

Called by Claude Code hooks with the event name as the first argument and the
hook payload as JSON on stdin. A run starts when the bold-mode skill or /bold
command is used, and ends when Claude finishes its turn (Stop).

Design rule: this script must never break the user's session. Any internal
error exits 0 silently (allow).

Settings (environment variables):
  BOLD_MODE_BUDGET   max counted steps per run (default 15)
  BOLD_MODE_GUARD    set to "off" to disable all blocking
"""
import json
import os
import re
import sys
import tempfile
import time

COUNTED_TOOLS = {"Bash", "Edit", "Write", "MultiEdit", "NotebookEdit"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
STALE_SECONDS = 6 * 60 * 60
WARN_AT_REMAINING = 3

START_PROMPT = re.compile(r"^\s*/(bold-mode:)?bold(\s|$)|\bbold-mode\b", re.IGNORECASE)

# Commands that are never allowed during a bold run, wherever they run.
ALWAYS_BLOCKED = [
    (r"\bgit\s+push\b[^\n;&|]*(--force\b|--force-with-lease\b|\s-f\b)", "force-push"),
    (r"\bgit\s+push\b[^\n;&|]*\b(main|master|production|prod|release)\b", "push to a protected branch"),
    (r"\b(npm|pnpm|yarn|cargo|gem)\s+publish\b|\btwine\s+upload\b", "publishing a package"),
    (r"\bvercel\b[^\n;&|]*--prod\b|\bnetlify\s+deploy\b[^\n;&|]*--prod\b", "production deploy"),
    (r"\b(fly|flyctl|firebase|serverless|sls)\s+deploy\b", "deploy"),
    (r"\bkubectl\s+(apply|delete|replace|scale)\b|\bhelm\s+(install|upgrade|uninstall)\b", "changing a cluster"),
    (r"\bterraform\s+(apply|destroy)\b|\bpulumi\s+(up|destroy)\b", "changing infrastructure"),
    (r"\bdocker\s+push\b|\bgh\s+release\s+create\b", "publishing an artifact"),
    (r"\bdrop\s+(table|database|schema)\b|\btruncate\s+table\b", "dropping data"),
    (r"\b(prisma\s+migrate\s+deploy|rails\s+db:(drop|migrate)|alembic\s+upgrade)\b", "migrating a database"),
    (r"\brm\s+-[a-z]*r[a-z]*\s+(/|~|\$HOME)(\s|$)", "deleting a root or home folder"),
]

# Commands that are only blocked when run inside the original folder.
ORIGINAL_ONLY_BLOCKED = [
    (r"\bgit\s+reset\s+--hard\b", "hard reset of the original"),
    (r"\bgit\s+clean\s+-[a-z]*f", "cleaning the original"),
    (r"\bgit\s+(checkout|restore)\s+(--\s+)?\.(\s|$)", "discarding changes in the original"),
    (r"\bgit\s+merge\b", "merging into the original"),
    (r"\brm\s+-[a-z]*r", "recursive delete in the original"),
]


def state_dir():
    path = os.path.join(tempfile.gettempdir(), "bold-mode")
    os.makedirs(path, exist_ok=True)
    return path


def state_path(session_id):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "default")
    return os.path.join(state_dir(), safe + ".json")


def load_state(session_id):
    try:
        with open(state_path(session_id)) as f:
            state = json.load(f)
    except (OSError, ValueError):
        return None
    if time.time() - state.get("started", 0) > STALE_SECONDS:
        clear_state(session_id)
        return None
    return state


def save_state(session_id, state):
    with open(state_path(session_id), "w") as f:
        json.dump(state, f)


def clear_state(session_id):
    try:
        os.remove(state_path(session_id))
    except OSError:
        pass


def budget():
    try:
        return max(1, int(os.environ.get("BOLD_MODE_BUDGET", "15")))
    except ValueError:
        return 15


def guard_enabled():
    return os.environ.get("BOLD_MODE_GUARD", "on").lower() not in ("off", "0", "false")


def start_run(payload):
    state = {
        "started": time.time(),
        "steps": 0,
        "root": os.path.realpath(payload.get("cwd") or os.getcwd()),
    }
    save_state(payload.get("session_id"), state)
    return state


def is_bold_skill(payload):
    if payload.get("tool_name") != "Skill":
        return False
    tool_input = payload.get("tool_input") or {}
    return "bold-mode" in str(tool_input.get("skill", "")) + str(tool_input.get("command", ""))


def inside_original(path, root):
    """True if path is in the original folder and not in a bold-* isolation folder."""
    real = os.path.realpath(path)
    try:
        rel = os.path.relpath(real, root)
    except ValueError:  # different drive on Windows
        return False
    if rel == "." or rel.startswith(".."):
        return rel == "."
    first = rel.split(os.sep)[0]
    return not (first.startswith("bold-") or first.startswith(".bold"))


def deny(reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "bold-mode guard: " + reason,
        }
    }


def check_blast_radius(payload, state):
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    root = state["root"]

    if tool in WRITE_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if path:
            if not os.path.isabs(path):
                path = os.path.join(payload.get("cwd") or root, path)
            if inside_original(path, root):
                return (
                    "this edit targets the original (" + path + "). Bold work must happen in the "
                    "isolated copy: a git worktree like ../<repo>-bold-<topic>, or /tmp/bold-<topic>. "
                    "Create it, then edit there."
                )

    if tool == "Bash":
        command = tool_input.get("command", "")
        for pattern, label in ALWAYS_BLOCKED:
            if re.search(pattern, command, re.IGNORECASE):
                return "blocked " + label + " during a bold run. Leave it for the user to decide."
        cwd = os.path.realpath(payload.get("cwd") or root)
        cd = re.match(r"^\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", command)
        if cd:
            target = os.path.expanduser(cd.group(1).strip("\"'"))
            cwd = os.path.realpath(os.path.join(cwd, target))
        if inside_original(cwd, root):
            for pattern, label in ORIGINAL_ONLY_BLOCKED:
                if re.search(pattern, command, re.IGNORECASE):
                    return "blocked " + label + ". Run it inside the isolated copy instead."
    return None


def on_user_prompt(payload):
    if START_PROMPT.search(payload.get("prompt", "")):
        start_run(payload)
    return None


def on_pre_tool(payload):
    session = payload.get("session_id")
    state = load_state(session)

    if is_bold_skill(payload):
        if state is None:
            start_run(payload)
        return None
    if state is None or not guard_enabled():
        return None

    tool = payload.get("tool_name")
    if tool not in COUNTED_TOOLS:
        return None

    limit = budget()
    if state["steps"] >= limit:
        return deny(
            "the step budget (" + str(limit) + ") is used up. Stop building now and write the "
            "report with what you have: the table, what was learned, and where the result lives."
        )

    problem = check_blast_radius(payload, state)
    if problem:
        return deny(problem)

    state["steps"] += 1
    save_state(session, state)
    return None


def on_post_tool(payload):
    state = load_state(payload.get("session_id"))
    if state is None or payload.get("tool_name") not in COUNTED_TOOLS:
        return None
    remaining = budget() - state["steps"]
    if 0 < remaining <= WARN_AT_REMAINING:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "bold-mode: " + str(remaining) + " step(s) left in the budget. "
                "Wrap up, measure, and prepare the report.",
            }
        }
    return None


def on_stop(payload):
    clear_state(payload.get("session_id"))
    return None


HANDLERS = {
    "UserPromptSubmit": on_user_prompt,
    "PreToolUse": on_pre_tool,
    "PostToolUse": on_post_tool,
    "Stop": on_stop,
}


def main():
    try:
        payload = json.load(sys.stdin)
        event = sys.argv[1] if len(sys.argv) > 1 else payload.get("hook_event_name", "")
        result = HANDLERS.get(event, lambda p: None)(payload)
        if result:
            print(json.dumps(result))
    except Exception:  # never break the user's session
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
