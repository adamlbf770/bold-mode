# From scratch today

**Works for:** code, architecture, design, writing

**The move:** Ignore how it got here. If you built it today, with today's tools and today's requirements, what would it look like?

**Ask:**
- Which parts exist only because of a requirement that no longer applies?
- What do modern libraries or platforms now do for free?
- What would a newcomer find strange about the current shape?

**Example:** A hand-rolled date-parsing module from 2015 → the platform's built-in `Intl`/`Temporal` APIs.

**Watch out:** Rewrites hide migration cost. Always fill in the "effort to adopt" row honestly.
