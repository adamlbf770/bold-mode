import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid

GUARD = os.path.join(os.path.dirname(__file__), "..", "hooks", "guard.py")


def run(event, payload, env=None):
    full_env = dict(os.environ)
    full_env.pop("BOLD_MODE_BUDGET", None)
    full_env.pop("BOLD_MODE_GUARD", None)
    full_env.update(env or {})
    out = subprocess.run(
        [sys.executable, GUARD, event],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=full_env,
    )
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout) if out.stdout.strip() else None


def denied(result):
    return bool(result) and result["hookSpecificOutput"].get("permissionDecision") == "deny"


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.session = "test-" + uuid.uuid4().hex
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.base = {"session_id": self.session, "cwd": self.root}

    def tearDown(self):
        run("Stop", self.base)

    def start(self, via="skill"):
        if via == "skill":
            run("PreToolUse", {**self.base, "tool_name": "Skill", "tool_input": {"skill": "bold-mode:bold-mode"}})
        else:
            run("UserPromptSubmit", {**self.base, "prompt": "/bold the cache layer"})

    def bash(self, command, cwd=None, env=None):
        return run("PreToolUse", {**self.base, "cwd": cwd or self.root, "tool_name": "Bash",
                                  "tool_input": {"command": command}}, env)

    def write(self, path, env=None):
        return run("PreToolUse", {**self.base, "tool_name": "Write",
                                  "tool_input": {"file_path": path, "content": "x"}}, env)

    # --- inactive by default ---
    def test_inactive_without_a_run(self):
        self.assertIsNone(self.write(os.path.join(self.root, "a.py")))
        self.assertIsNone(self.bash("git push --force origin main"))

    def test_unrelated_prompt_does_not_start(self):
        run("UserPromptSubmit", {**self.base, "prompt": "please fix the typo, be careful"})
        self.assertIsNone(self.write(os.path.join(self.root, "a.py")))

    # --- start triggers ---
    def test_slash_command_starts_run(self):
        self.start(via="prompt")
        self.assertTrue(denied(self.write(os.path.join(self.root, "a.py"))))

    # --- blast radius ---
    def test_blocks_write_to_original(self):
        self.start()
        self.assertTrue(denied(self.write(os.path.join(self.root, "src", "a.py"))))

    def test_relative_path_resolved_against_cwd(self):
        self.start()
        self.assertTrue(denied(self.write("src/a.py")))

    def test_allows_write_in_tmp_copy(self):
        self.start()
        self.assertIsNone(self.write(os.path.join(tempfile.gettempdir(), "bold-cache", "a.py")))

    def test_allows_write_in_sibling_worktree(self):
        self.start()
        sibling = os.path.join(os.path.dirname(self.root), "repo-bold-cache", "a.py")
        self.assertIsNone(self.write(sibling))

    def test_allows_bold_subfolder_inside_original(self):
        self.start()
        self.assertIsNone(self.write(os.path.join(self.root, ".bold", "cache", "a.py")))

    def test_always_blocked_commands(self):
        self.start()
        for cmd in ["git push --force origin bold/x", "git push origin main", "npm publish",
                    "vercel --prod", "terraform apply", "kubectl apply -f x.yaml",
                    "psql -c 'DROP TABLE users'", "rm -rf ~"]:
            with self.subTest(cmd=cmd):
                self.assertTrue(denied(self.bash(cmd, cwd="/tmp")))

    def test_safe_commands_allowed(self):
        self.start()
        for cmd in ["git worktree add ../repo-bold-x -b bold/x", "npm test", "git push origin bold/x",
                    "cp -r . /tmp/bold-x", "pytest -q"]:
            with self.subTest(cmd=cmd):
                self.assertIsNone(self.bash(cmd))

    def test_reset_blocked_in_original_but_allowed_in_copy(self):
        self.start()
        self.assertTrue(denied(self.bash("git reset --hard")))
        self.assertTrue(denied(self.bash("cd " + self.root + " && git reset --hard", cwd="/tmp")))
        self.assertIsNone(self.bash("git reset --hard", cwd=os.path.join(tempfile.gettempdir(), "bold-x")))

    def test_guard_off(self):
        self.start()
        self.assertIsNone(self.write(os.path.join(self.root, "a.py"), env={"BOLD_MODE_GUARD": "off"}))

    # --- budget ---
    def test_budget_enforced(self):
        self.start()
        env = {"BOLD_MODE_BUDGET": "3"}
        for _ in range(3):
            self.assertIsNone(self.bash("npm test", env=env))
        result = self.bash("npm test", env=env)
        self.assertTrue(denied(result))
        self.assertIn("budget", result["hookSpecificOutput"]["permissionDecisionReason"])

    def test_default_budget_is_25(self):
        self.start()
        for _ in range(25):
            self.assertIsNone(self.bash("npm test"))
        self.assertTrue(denied(self.bash("npm test")))

    def test_bold_go_starts_fresh_run_after_checkpoint(self):
        self.start()
        run("Stop", self.base)  # checkpoint ends the turn
        run("UserPromptSubmit", {**self.base, "prompt": "/bold go"})
        self.assertTrue(denied(self.write(os.path.join(self.root, "a.py"))))

    def test_isolation_snapshot_commands_allowed(self):
        self.start()
        self.assertIsNone(self.bash("git status --porcelain"))
        self.assertIsNone(self.bash(
            'base=$(git stash create); git worktree add ../app-bold-x -b bold/x ${base:-HEAD}'))

    def test_reads_are_free(self):
        self.start()
        env = {"BOLD_MODE_BUDGET": "1"}
        for _ in range(5):
            self.assertIsNone(run("PreToolUse", {**self.base, "tool_name": "Read",
                                                 "tool_input": {"file_path": "x"}}, env))
        self.assertIsNone(self.bash("npm test", env=env))

    def test_warning_near_end(self):
        self.start()
        env = {"BOLD_MODE_BUDGET": "4"}
        self.bash("npm test", env=env)
        post = run("PostToolUse", {**self.base, "tool_name": "Bash", "tool_input": {}}, env)
        self.assertIn("3 step(s) left", post["hookSpecificOutput"]["additionalContext"])

    def test_stop_ends_run(self):
        self.start()
        run("Stop", self.base)
        self.assertIsNone(self.write(os.path.join(self.root, "a.py")))

    # --- robustness ---
    def test_garbage_input_never_blocks(self):
        out = subprocess.run([sys.executable, GUARD, "PreToolUse"], input="not json",
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
