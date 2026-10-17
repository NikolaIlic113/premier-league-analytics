# Data Dictionary

This document describes the **26 columns** in `data/processed/matches.csv` (13,166 match records, seasons 1992/93–2025/26). Types below are **logical analytical types**, not necessarily the physical pandas dtype: nullable integer-like columns can be read as `float64` because CSV blanks are represented as `NaN`.

| Column | Logical type | Description |
|---|---|---|
| `MatchID` | Integer | Unique identifier assigned to each processed match |
| `Season` | Text | Season label, e.g. `1992/93` |
| `Date` | Date | Match date, stored as `YYYY-MM-DD` |
| `HomeTeam` | Text | Home club name as standardized in the processed file |
| `AwayTeam` | Text | Away club name as standardized in the processed file |
| `FTHG` | Integer | Full-time home goals |
| `FTAG` | Integer | Full-time away goals |
| `FTR` | Text | Full-time result: `H` home win, `D` draw, `A` away win |
| `_source_file` | Text | Raw season CSV filename |
| `_source_row` | Integer | Row number in the raw source file |
| `HTHG` | Nullable integer | Half-time home goals |
| `HTAG` | Nullable integer | Half-time away goals |
| `HTR` | Text / null | Half-time result: `H`, `D`, `A` |
| `HS` | Nullable integer | Home shots |
| `AS` | Nullable integer | Away shots |
| `HST` | Nullable integer | Home shots on target |
| `AST` | Nullable integer | Away shots on target |
| `HF` | Nullable integer | Home fouls |
| `AF` | Nullable integer | Away fouls |
| `HC` | Nullable integer | Home corners |
| `AC` | Nullable integer | Away corners |
| `HY` | Nullable integer | Home yellow cards |
| `AY` | Nullable integer | Away yellow cards |
| `HR` | Nullable integer | Home red cards |
| `AR` | Nullable integer | Away red cards |
| `Referee` | Text / null | Referee name |

## Availability by season

| Season range | Match results | Half-time results | Match statistics and referee |
|---|---|---|---|
| 1992/93–1994/95 | Yes | Not populated | Not populated |
| 1995/96–1999/00 | Yes | Yes | Not populated |
| 2000/01–2025/26 | Yes | Yes | Yes |

Null historical values mean the information is unavailable in the assembled source data, **not zero**. `MatchID` identifies rows in the current processed build and should not be treated as a permanent external match identifier.
