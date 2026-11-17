# Contributing

Thanks for helping. Small, focused pull requests are best.

## Add a lens (easiest, ~10 minutes)

A lens is one reframing move that has helped you find a better solution.

1. Copy the template from [`skills/bold-mode/lenses/README.md`](skills/bold-mode/lenses/README.md).
2. Save it as `skills/bold-mode/lenses/<short-kebab-name>.md`.
3. Add one row to the index table in that README.
4. Open a pull request.

A good lens:

- names **one** move, not a list of tips,
- has 2-4 questions that actually change how you look at the problem,
- has a concrete before → after example,
- says honestly when it leads somewhere bad ("Watch out").

Lenses for design, writing, data, infrastructure and specific stacks (React, Django, Rails, Go, …) are especially welcome.

## Improve the guard

The guard is `hooks/guard.py`, standard-library Python only. If you add or change a blocked pattern:

1. Add a test in `tests/test_guard.py` (one that should be blocked, one similar command that should pass).
2. Run `python3 -m unittest discover -s tests`.

The guard must never break a session: any internal error must exit 0 without output.

## Share a real report

Ran bold-mode on something real? Open an issue with the report table (remove anything private). Real results, especially ones where Bold lost, help everyone calibrate.

## Translations

`README.<lang>.md` files are welcome. Keep them short.
