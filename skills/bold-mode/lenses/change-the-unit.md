# Change the unit

**Works for:** code, architecture, design

**The move:** Change the unit of work: one item vs a batch, a stream vs a file, a page vs a list, per user vs per team.

**Ask:**
- What is the current unit, and why that one?
- What if the system handled 1000 at a time, or one at a time as they arrive?
- What if the user worked on a set instead of an item?

**Example:** Sending one email API call per user → one batched call per 500 users; the rate-limit code disappears.

**Watch out:** Bigger units mean bigger failures. Say what happens when one item in the batch fails.
