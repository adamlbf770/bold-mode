# Ten x

**Works for:** code, architecture

**The move:** Design for 10x the load, 10x the users, or 1/10 of the code. The constraint forces a different shape.

**Ask:**
- What would break first at 10x the load?
- What would you keep if you had to write it in 1/10 of the lines?
- Which of those changes is cheap today?

**Example:** A 900-line export feature rewritten under a 90-line limit → stream rows straight to CSV; no intermediate model.

**Watch out:** Don't ship the 10x architecture if the 1x need is real. Use it to find ideas, then scale back.
