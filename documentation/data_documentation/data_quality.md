# Data Quality and Validation

## Scope

The current validation script, `scripts/validate_matches.py`, reads **only** `data/processed/matches.csv`. It does not reprocess the RAW files. It writes:

- `documentation/data_validation/matches_validation_summary.csv` — one row per expected season, with match counts, team counts, home/away balance, first/last date and a structural PASS/FAIL status.
- `documentation/data_validation/matches_validation_issues.csv` — individual rule violations, including source match details and issue codes.

Run from the project root:

```powershell
python scripts/validate_matches.py
```

## Implemented checks

The validator checks required columns; valid dates and season labels; non-null core match fields; nonempty and distinct home/away teams; unique integer match IDs; duplicate home/away fixtures within a season; nonnegative whole-number goals; full-time and half-time result consistency; date years within the season span; historical availability of half-time and statistics fields; nonnegative integer match statistics; shots on target not exceeding total shots; and expected season structure.

For 1992/93–1994/95, it expects 22 teams and 462 matches per season. For 1995/96 onward, it expects 20 teams and 380 matches per season. It also checks each club's home and away match counts, the expected 34 seasons, and the total 13,166 matches.

**Scope note:** This is a defined set of programmatic checks, not a guarantee that every source value is accurate. The script does not comprehensively verify club-name identity against an independent canonical team list.

## Current known issues

The last documented validation produced **five rule violations affecting three matches**, all related to shots on target exceeding total shots:

| Season | Match | Issue(s) |
|---|---|---|
| 2000/01 | Coventry – Tottenham | Home and away shots mismatch |
| 2000/01 | Bradford – Charlton | Home and away shots mismatch |
| 2021/22 | Newcastle – West Ham | Away shots mismatch |

The 34 season-structure checks pass. The validator nevertheless prints **`VALIDATION FAIL`** and exits with code 1 whenever any issue is present, including these known source anomalies. This is expected for the current dataset and should not be misrepresented as a clean validation pass.

## Handling policy

- Keep the original RAW files unchanged.
- Do not silently overwrite or fabricate suspicious source values to make validation pass.
- Retain `matches_validation_issues.csv` as an audit record.
- Preserve unavailable historical statistics as null rather than zero.
- Re-run validation after rebuilding or changing the processed dataset.
