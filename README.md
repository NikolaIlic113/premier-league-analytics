# Premier League Analytics

A Python and Power BI analytics project covering English Premier League match data from **1992/93 through 2025/26**.

## Current dataset

- **34 seasons**, **13,166 matches**, **26 columns**
- Seasons 1992/93–1994/95: 22 teams and 462 matches per season
- Seasons 1995/96 onward: 20 teams and 380 matches per season
- Processed output: `data/processed/matches.csv`
- 2025/26 data reflects the source snapshot used in the current build; do not assume the season is complete without refreshing the source.

## Sources

- [RSSSF](https://www.rsssf.org/tablese/eng93.html) — 1992/93 results
- [Football-Data.co.uk](https://www.football-data.co.uk/) — 1993/94 onward

See [`data_sources.md`](documentation/data_documentation/data_sources.md) for collection and provenance details.

## Project structure

```text
premier-league-analytics/
├── data/
│   ├── raw/                       # Source CSV files (ignored by Git)
│   └── processed/
│       └── matches.csv
├── documentation/
│   ├── data_documentation/
│   │   ├── data_dictionary.md
│   │   ├── data_quality.md
│   │   └── data_sources.md
│   └── data_validation/
│       ├── matches_validation_issues.csv
│       └── matches_validation_summary.csv
├── scripts/
│   ├── download_1992_93.py
│   ├── download_data.py
│   ├── build_match_dataset.py
│   └── validate_matches.py
├── notebooks/
├── powerbi/
├── .gitignore
└── README.md
```

## Rebuild and validate

Run from the project root with a Python environment that has the required packages installed (including `pandas`, `numpy` and `requests`):

```powershell
python scripts/download_1992_93.py
python scripts/download_data.py
python scripts/build_match_dataset.py
python scripts/validate_matches.py
```

The download scripts retrieve source data, the builder produces `matches.csv`, and the validator writes two CSV reports under `documentation/data_validation/`. The validator currently reports **five known shots-statistic inconsistencies across three matches**; season-structure checks pass. The original values are intentionally retained. See [`data_quality.md`](documentation/data_documentation/data_quality.md).

## Documentation

- [Data dictionary](documentation/data_documentation/data_dictionary.md)
- [Data sources](documentation/data_documentation/data_sources.md)
- [Data quality](documentation/data_documentation/data_quality.md)
- [Validation summary](documentation/data_validation/matches_validation_summary.csv)
- [Known issues](documentation/data_validation/matches_validation_issues.csv)

## Technologies and next steps

Python, pandas, NumPy, Jupyter Notebook, Git/GitHub and Power BI. Next steps include preparing a Power BI data model and developing reporting pages.

**Data-use note:** Check source-provider terms before publishing or redistributing the processed match dataset.
