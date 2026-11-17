# Make it boring

**Works for:** code, architecture

**The move:** Replace custom, clever code with the most standard, boring tool that does the job.

**Ask:**
- Is there a standard library function, well-known package, or platform feature for this?
- Which part of this code would a new team member need explained?
- What is custom here only out of habit?

**Example:** A homemade job queue with retries and locks → the database's built-in `SKIP LOCKED` queue pattern or a standard queue library.

**Watch out:** A new dependency is a cost too. Count it in the table.
