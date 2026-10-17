# Data Sources

## Coverage

The processed dataset contains 13,166 English Premier League matches across 34 seasons, from **1992/93 through 2025/26**. The 2025/26 file represents the source data captured when the dataset was built; it should not be assumed to be a final, completed season without a subsequent refresh.

## Source websites

| Seasons | Source | Purpose |
|---|---|---|
| 1992/93 | [RSSSF — England 1992/93](https://www.rsssf.org/tablese/eng93.html) | Historical match results for the inaugural Premier League season |
| 1993/94–2025/26 | [Football-Data.co.uk](https://www.football-data.co.uk/) | Match results and, where available, half-time scores, match statistics and referees |

The scripts `scripts/download_1992_93.py` and `scripts/download_data.py` handle the respective sources. The first season requires a separate extraction process because its source format differs from the Football-Data CSV files.

## Pipeline and provenance

1. Download source files into `data/raw/` (one CSV per season).
2. Run `scripts/build_match_dataset.py` to harmonize the seasons and write `data/processed/matches.csv`.
3. Run `scripts/validate_matches.py` to validate the processed dataset and produce reports in `documentation/data_validation/`.

The processed dataset includes `_source_file` and `_source_row` to trace each match back to its raw source file and row. `data/raw/` is excluded from Git tracking by `.gitignore`.

## Historical limitations

- The earliest seasons have match results but not the later match-statistics fields.
- Half-time results are populated from 1995/96 onward; the statistics and referee fields in the current dataset are populated from 2000/01 onward.
- Missing historical fields remain null; they are not filled with invented values.
- Source data may contain inconsistencies. Known issues are recorded in `documentation/data_validation/matches_validation_issues.csv` rather than silently corrected.

Consult each provider's terms before redistributing source-derived datasets. The presence of a local CSV or a public website does not itself establish redistribution rights.
