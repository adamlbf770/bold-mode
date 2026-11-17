# Delete a layer

**Works for:** code, architecture

**The move:** Remove a whole layer (wrapper, service, abstraction, cache, config system) instead of improving it.

**Ask:**
- Which layer only forwards calls or renames things?
- What breaks if this layer is gone, and can the callers handle it directly?
- Is this abstraction used by more than one real caller?

**Example:** A `UserRepository` wrapping an ORM that already does the same queries → callers use the ORM directly; 400 lines removed.

**Watch out:** Layers that enforce security, validation or transactions usually exist for a reason. Check before deleting.
