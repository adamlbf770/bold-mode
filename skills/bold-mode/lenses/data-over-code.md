# Data over code

**Works for:** code

**The move:** Replace branching logic with a table, map, or config that the code just reads.

**Ask:**
- Are there long if/else or switch chains that differ only by values?
- Could a non-programmer edit these rules if they were data?
- Would a table make missing cases obvious?

**Example:** A 60-line `getShippingPrice` with nested ifs → a 12-row price table and a 5-line lookup.

**Watch out:** Tables hide logic from type checkers and tests. Add a check that every row is valid.
