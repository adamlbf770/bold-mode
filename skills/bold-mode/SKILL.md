---
name: bold-mode
description: Use only when the user explicitly asks to reinvent or radically rethink code, a design, text or architecture, says "be bold" or "take risks", or runs /bold. Risk is allowed in the idea, not in the blast radius. Do NOT use for small fixes, bug fixes or routine refactors.
---

# Bold Mode

**Risk is allowed in the idea, not in the blast radius.**

Goal: go beyond the safe, conventional answer and try a genuinely different approach, without putting the user's working material at risk. Then prove, with measurements, whether it was worth it.

## When to use

- The user explicitly asks to rethink, reinvent, or radically improve something, says "be bold" / "take risks", or runs `/bold`.
- Or: two conventional attempts have already failed, or the result is clearly over-complicated.

**Do NOT use for:** small fixes, bug fixes, typos, single-function tweaks, routine refactors, or anything the user described as stable and working. Use the normal approach there.

## Definitions

- **Cheap** = under 30 minutes of work or under 200 changed lines. Anything above that is not cheap.
- **Step** = a tool call that changes or measures something (Bash, Edit, Write). Reading files is free.
- **Budget** = 15 steps for the whole run (the user may set another number with `BOLD_MODE_BUDGET`). If the bold version is not stable by then, or still fails after 3 fix attempts, stop and report what was learned. Never extend the budget on your own.

If the bold-mode plugin's guard hook is installed, it counts steps and blocks writes to the original. Treat a block as a signal to stop or re-isolate, never as an obstacle to work around.

## Steps

1. **Isolate.** Never touch the original.
   - Git repo: `git worktree add ../<repo>-bold-<topic> -b bold/<topic>` and work only inside that folder.
   - No repo: copy the folder to `/tmp/bold-<topic>` (or `$TMPDIR/bold-<topic>`) and work only there.
   - Never force-push, push to main, delete or migrate data, publish, or deploy.
2. **Baseline.** In the isolated copy, run the existing tests and record the result. If the baseline is red, say so before going on.
   - No tests: write 2-3 quick checks that capture current behavior. If even that is impossible, say so and state that the comparison will be weaker.
3. **Diverge.** Read 2-3 files from `lenses/` (next to this file) that fit the problem. Then write down three ideas before choosing:
   - **Safe:** the conventional improvement.
   - **Bold:** a different architecture, algorithm, library, data shape, or deleting a whole layer.
   - **Wild:** challenge a core assumption (what if this part did not exist? what if it were built from scratch today?).
4. **Build Bold.** Prefer the version that deletes things over the one that adds things. Build Wild too only if it is cheap. Build Safe only if it is cheap; otherwise describe it with an estimate clearly marked "not built".
5. **Measure** every built version against the baseline with the same checks, plus the numbers that matter (see "Measuring"). Never claim an improvement without a number.
6. **Report** one table:

   | | Baseline | Bold | Safe | Wild |
   |---|---|---|---|---|
   | Checks passing | | | measured or "not built" | if built |
   | Size / complexity | | | | |
   | Speed (if relevant) | | | | |
   | Risk to adopt | | | | |
   | Effort to adopt | | | | |

   Say plainly if Bold lost. A failed experiment that taught something is a valid result.
7. **Hand over.** Leave the branch or copy for review. Do not merge, copy back, or replace anything.

## Measuring

The same approach works beyond code. Only the measuring changes:

- **Code:** tests passing, lines changed, dependencies, speed.
- **Architecture:** number of components, dependencies, failure modes, migration cost.
- **Design / UI:** a checklist of the user's stated goals, scored side by side with the original.
- **Writing:** length plus a rubric (clarity, tone, goal met), side by side with the original.

If no honest measurement exists, say so instead of claiming improvement.

## Boundaries

Bold applies to design and implementation choices. It never applies to security, data safety, money, credentials, or irreversible actions. For those, stop and ask.

## Output

Finish with: what was tried (and which lenses), the table, a one-line recommendation (adopt Bold / adopt Safe / keep Baseline), and where the result lives (branch name or folder path).
