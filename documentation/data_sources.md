# Data Sources

## Primary Source

### Football-Data.co.uk

Website:
https://www.football-data.co.uk/

Coverage:
Premier League data from the 1993/94 season onwards.

Primary use:
- Match results
- Half-time results
- Match statistics
- Referee information
- Other historical match-level information where available

## Data Collection

Data will be downloaded programmatically using Python.

Raw source files will be stored locally in `data/raw/` and excluded from Git version control.

## Data Limitations

Historical seasons do not contain the same set of variables.

Additional match statistics become available in later seasons, while older seasons contain fewer variables.