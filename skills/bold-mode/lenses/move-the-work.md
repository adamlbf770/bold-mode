# Move the work

**Works for:** code, architecture

**The move:** Do the work at a different time or place: build time instead of run time, database instead of app, client instead of server, once instead of every request.

**Ask:**
- What is computed again and again with the same result?
- What could be computed before the user asks?
- Which system is best placed to do this work?

**Example:** Markdown rendered on every page view → rendered once at build time; the server becomes static files.

**Watch out:** Moved work can go stale. Say how it gets refreshed.
