---
name: bold-mode
description: Use only when the user explicitly asks to reinvent or radically rethink code, a design, text or architecture, says "be bold" or "take risks", or runs /bold. Risk is allowed in the idea, not in the blast radius. Do NOT use for small fixes, bug fixes or routine refactors.
---

# Bold Mode

**Risk is allowed in the idea, not in the blast radius.**

Goal: go beyond the safe, conventional answer and try a genuinely different approach, without putting the user's working material at risk. Then prove, with measurements, whether it was worth it.

## When to use

- The user explicitly asks to rethink, reinvent, or radically improve something, says "be bold" / "take risks", or runs `/bold`.

**Never start on your own.** If two conventional attempts have already failed, or the result is clearly over-complicated, *offer* it in one line ("Want me to try this in bold mode? It runs isolated and reports back.") and wait for a yes.

**Do NOT use for:** small fixes, bug fixes, typos, single-function tweaks, routine refactors, or anything the user described as stable and working. Use the normal approach there.

## Definitions

- **Cheap** = at most 200 changed lines and at most 5 steps to build. Anything above that is not cheap. (Do not estimate in minutes: you cannot measure time.)
- **Step** = a tool call that changes or measures something (Bash, Edit, Write). Reading files is free.
- **Budget** = 25 steps per run (the user may set another number with `BOLD_MODE_BUDGET`). Rough split: isolate + baseline ≈ 5, build ≈ 12, measure + report ≈ 8. If the bold version is not stable by then, or still fails after 3 fix attempts, stop and report what was learned. Never extend the budget on your own.
- **Risk to adopt** (used in the report):
  - **low**: same observable behavior, all checks pass, easy to revert.
  - **medium**: behavior or interfaces change in ways the checks cover, or one new dependency.
  - **high**: behavior changes the checks do not cover, data or migration involved, or hard to revert.
  Always add a short reason after the level.

If the bold-mode plugin's guard hook is installed, it counts steps and blocks writes to the original. Treat a block as a signal to stop or re-isolate, never as an obstacle to work around.

## Steps

1. **Isolate.** Never touch the original.
   - Git repo: first run `git status --porcelain`.
     - Clean: `git worktree add ../<repo>-bold-<topic> -b bold/<topic>`.
     - Uncommitted changes: snapshot them without touching the working tree, and branch from the snapshot:
       `base=$(git stash create); git worktree add ../<repo>-bold-<topic> -b bold/<topic> ${base:-HEAD}`.
       Tell the user that untracked files are not included in the copy.
   - No repo: copy the folder to `/tmp/bold-<topic>` (or `$TMPDIR/bold-<topic>`), excluding dependency and build folders (`node_modules`, `.venv`, `venv`, `dist`, `build`, `target`, `.next`), e.g. `rsync -a --exclude node_modules --exclude .venv ... ./ /tmp/bold-<topic>/`. Reinstall dependencies in the copy only if the baseline needs them.
   - Work only inside the copy. Never force-push, push to the default branch (whatever it is called: main, master, develop…), delete or migrate data, publish, or deploy.
2. **Baseline.** In the isolated copy, run the existing tests and record the result. If the baseline is red, say so before going on.
   - No tests: write 2-3 quick checks that capture current behavior. If even that is impossible, say so and state that the comparison will be weaker.
   - For design or writing: write the scoring rubric **now**, before any alternative exists, from the user's stated goals. You may not change it later.
3. **Diverge.** Read 2-3 files from `lenses/` (next to this file) that fit the problem. Then write down three ideas before choosing:
   - **Safe:** the conventional improvement.
   - **Bold:** a different architecture, algorithm, library, data shape, or deleting a whole layer.
   - **Wild:** challenge a core assumption (what if this part did not exist? what if it were built from scratch today?).
4. **Checkpoint (only if Bold is not cheap).** Show the three ideas, which one you picked and why, and an estimate (lines, steps). End the turn with: "Reply `/bold go` to build it, or name another idea." If Bold is cheap, skip this and go straight on.
   - On `/bold go`, continue from the plan in the previous message, in the same isolated copy. A fresh budget starts there.
5. **Build Bold.** Prefer the version that deletes things over the one that adds things. Build Wild too only if it is cheap. Build Safe only if it is cheap; otherwise describe it with an estimate clearly marked "not built".
6. **Measure** every built version against the baseline with the same checks, plus the numbers that matter (see "Measuring"). Never claim an improvement without a number.
7. **Report** one table:

   | | Baseline | Bold | Safe | Wild |
   |---|---|---|---|---|
   | Checks passing | | | measured or "not built" | if built |
   | Size / complexity | | | | |
   | Speed (if relevant) | | | | |
   | Risk to adopt | – | level + reason | | |
   | Effort to adopt | – | | | |

   Say plainly if Bold lost. A failed experiment that taught something is a valid result.
8. **Hand over.** Leave the branch or copy for review. Do not merge, copy back, or replace anything.

## Measuring

The same approach works beyond code. Only the measuring changes:

- **Code:** tests passing, lines changed, dependencies, speed.
- **Architecture:** number of components, dependencies, failure modes, migration cost.
- **Design / UI:** score against the rubric written in step 2, side by side with the original.
- **Writing:** length plus the rubric written in step 2 (clarity, tone, goal met), side by side with the original.

You are grading your own work, which is biased. For design and writing, also show the two versions to the user labelled **A** and **B** in random order, without saying which is the original, and let them pick before you reveal which is which.

If no honest measurement exists, say so instead of claiming improvement.

## Boundaries

Bold applies to design and implementation choices. It never applies to security, data safety, money, credentials, or irreversible actions. For those, stop and ask.

## Output

Finish with:

1. What was tried, and which lenses.
2. The table.
3. A one-line recommendation: adopt Bold / adopt Safe / keep Baseline.
4. Where the result lives (branch name or folder path) and the exact commands to review and adopt it, for example:
   - Review: `git diff <default-branch>...bold/<topic>`
   - Adopt: `git merge bold/<topic>` (run by the user, not by you)
   - Discard: `git worktree remove ../<repo>-bold-<topic> && git branch -D bold/<topic>`
   - For a `/tmp` copy: `diff -ru <original> /tmp/bold-<topic>` to review, and `rm -rf /tmp/bold-<topic>` to discard.
