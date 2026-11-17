# Changelog

## 1.1.0

- Never auto-start: after two failed conventional attempts, Claude now offers bold mode and waits for a yes.
- "Cheap" is defined in lines and steps instead of minutes, which an agent cannot measure.
- Default step budget raised from 15 to 25, with a rough split per phase.
- Isolation handles uncommitted changes (`git stash create` snapshot, working tree untouched) and skips dependency/build folders when copying to `/tmp`.
- "Default branch" instead of "main".
- Checkpoint after Diverge when Bold is not cheap; continue with `/bold go`.
- Design and writing rubrics are written before building, plus a blind A/B pick by the user.
- "Risk to adopt" has a defined low / medium / high scale.
- The report ends with exact review, adopt and discard commands.

## 1.0.0

- `bold-mode` skill: isolate, baseline, Safe / Bold / Wild, build, measure, report, hand over.
- 11 lenses for finding non-obvious ideas.
- Guard hook: step budget, blocks edits to the original, blocks force-push, push to main, publish, deploy, infra changes and data drops during a run.
- `/bold` command.
