# Invert the flow

**Works for:** code, architecture

**The move:** Flip the direction: pull instead of push, callee instead of caller, events instead of polling (or the reverse).

**Ask:**
- Who asks and who answers today? What if it were the other way around?
- Is something polling for changes that could be told about them?
- Is something pushing data nobody reads?

**Example:** A cron job polling every minute for new orders → the order service emits an event; the job disappears.

**Watch out:** Inverting often moves complexity rather than removing it. Measure where it ends up.
