# Sample report

> Illustrative example of the report format, not a measured result from a real project.

**Request:** `/bold the CSV export in src/export — it's slow and hard to change`

**Isolation:** `git worktree add ../shop-bold-export -b bold/export`

**Baseline:** 18/18 tests pass. Export of 50k orders: 41 s, peak memory 1.9 GB. `src/export`: 870 lines in 9 files.

**Lenses used:** change-the-unit, delete-a-layer, move-the-work

**Ideas**

- **Safe:** add pagination to the existing query, reuse the current model classes.
- **Bold** (change-the-unit + delete-a-layer): stream rows from the database cursor straight into the CSV writer; delete the intermediate `ExportRow` model and its mappers.
- **Wild** (move-the-work): keep a nightly pre-built export and serve it as a file.

**Built:** Bold (11 steps). Wild was cheap (under 200 lines) and was built too. Safe was not built.

| | Baseline | Bold | Safe | Wild |
|---|---|---|---|---|
| Tests passing | 18/18 | 18/18 | not built (estimate 18/18) | 15/18 (3 expect live data) |
| Lines in `src/export` | 870 | 190 | ~900 (estimate) | 240 |
| Export 50k orders | 41 s | 6 s | ~25 s (estimate) | 0.3 s |
| Peak memory | 1.9 GB | 60 MB | ~1 GB (estimate) | 40 MB |
| Risk to adopt | – | low: same output, checked byte-for-byte on 3 fixtures | low | high: data up to 24 h old |
| Effort to adopt | – | review one PR | half a day | needs a product decision |

**Recommendation:** adopt Bold. Wild is only worth it if a day-old export is acceptable, which is a product question.

**Result:** branch `bold/export`, worktree `../shop-bold-export`. Nothing merged.
