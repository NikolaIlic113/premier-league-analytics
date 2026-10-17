from pathlib import Path
import csv
import re
from datetime import datetime

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DATA_DIR / "matches.csv"
EXPECTED_SEASONS = {f"{year}/{(year + 1) % 100:02d}" for year in range(1992, 2026)}


# ============================================================
# SEASON GROUPS
# ============================================================

EARLY_SEASONS = {
    "1992/93",
    "1993/94",
    "1994/95",
}


HALF_TIME_SEASONS = {
    "1995/96",
    "1996/97",
    "1997/98",
    "1998/99",
    "1999/00",
}


# ============================================================
# COLUMN DEFINITIONS
# ============================================================

BASE_COLUMNS = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
]


HALF_TIME_COLUMNS = [
    "HTHG",
    "HTAG",
    "HTR",
]


STATISTICS_COLUMNS = [
    "HS",
    "AS",
    "HST",
    "AST",
    "HF",
    "AF",
    "HC",
    "AC",
    "HY",
    "AY",
    "HR",
    "AR",
]


REFEREE_COLUMN = [
    "Referee",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def season_from_filename(filename):
    """
    Convert filename:

        1992-93.csv

    into:

        1992/93
    """

    stem = Path(filename).stem

    match = re.match(
        r"^(\d{4})-(\d{2})$",
        stem
    )

    if match:
        return f"{match.group(1)}/{match.group(2)}"

    return stem


def get_relevant_columns(season):
    """
    Return the columns that should be included
    in the final dataset for a given season.
    """

    if season in EARLY_SEASONS:

        return BASE_COLUMNS.copy()

    if season in HALF_TIME_SEASONS:

        return (
            BASE_COLUMNS
            + HALF_TIME_COLUMNS
        )

    return (
        BASE_COLUMNS
        + HALF_TIME_COLUMNS
        + STATISTICS_COLUMNS
        + REFEREE_COLUMN
    )


def detect_encoding(filepath):
    """
    Try supported encodings and return the first
    encoding that can successfully read the file.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]

    for encoding in encodings:

        try:

            filepath.read_text(
                encoding=encoding
            )

            return encoding

        except UnicodeDecodeError:

            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Could not determine encoding for {filepath.name}"
    )


def parse_date(value):
    """
    Parse dates explicitly instead of relying on
    automatic date-format inference.

    Supported formats:

        YYYY-MM-DD
        YYYY/MM/DD
        DD/MM/YYYY
        DD/MM/YY
        DD-MM-YYYY
        DD-MM-YY

    Returns:
        pandas.Timestamp
        or pandas.NaT if invalid.
    """

    if value is None:
        return pd.NaT

    value = str(value).strip()

    if not value:
        return pd.NaT

    # --------------------------------------------------------
    # ISO format: YYYY-MM-DD
    # --------------------------------------------------------

    if re.fullmatch(
        r"\d{4}-\d{2}-\d{2}",
        value
    ):

        try:

            return pd.Timestamp(
                datetime.strptime(
                    value,
                    "%Y-%m-%d"
                )
            )

        except ValueError:

            return pd.NaT

    # --------------------------------------------------------
    # ISO-like format: YYYY/MM/DD
    # --------------------------------------------------------

    if re.fullmatch(
        r"\d{4}/\d{2}/\d{2}",
        value
    ):

        try:

            return pd.Timestamp(
                datetime.strptime(
                    value,
                    "%Y/%m/%d"
                )
            )

        except ValueError:

            return pd.NaT

    # --------------------------------------------------------
    # DD/MM/YYYY
    # --------------------------------------------------------

    if re.fullmatch(
        r"\d{2}/\d{2}/\d{4}",
        value
    ):

        try:

            return pd.Timestamp(
                datetime.strptime(
                    value,
                    "%d/%m/%Y"
                )
            )

        except ValueError:

            return pd.NaT

    # --------------------------------------------------------
    # DD/MM/YY
    # --------------------------------------------------------

    if re.fullmatch(
        r"\d{2}/\d{2}/\d{2}",
        value
    ):

        try:

            return pd.Timestamp(
                datetime.strptime(
                    value,
                    "%d/%m/%y"
                )
            )

        except ValueError:

            return pd.NaT

    # --------------------------------------------------------
    # DD-MM-YYYY
    # --------------------------------------------------------

    if re.fullmatch(
        r"\d{2}-\d{2}-\d{4}",
        value
    ):

        try:

            return pd.Timestamp(
                datetime.strptime(
                    value,
                    "%d-%m-%Y"
                )
            )

        except ValueError:

            return pd.NaT

    # --------------------------------------------------------
    # DD-MM-YY
    # --------------------------------------------------------

    if re.fullmatch(
        r"\d{2}-\d{2}-\d{2}",
        value
    ):

        try:

            return pd.Timestamp(
                datetime.strptime(
                    value,
                    "%d-%m-%y"
                )
            )

        except ValueError:

            return pd.NaT

    return pd.NaT


def clean_string(value):
    """
    Clean textual values.
    """

    if value is None:
        return ""

    value = str(value).strip()

    if value.lower() in {
        "",
        "nan",
        "none",
        "null",
    }:

        return ""

    return value


def clean_numeric(value):
    """
    Convert numeric values safely.

    Empty or invalid values become None.
    """

    value = clean_string(value)

    if not value:
        return None

    try:

        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except ValueError:

        return None


def read_csv_preserve_rows(filepath):
    """
    Read CSV using Python's csv module.

    Important:
    We deliberately do NOT use pandas on_bad_lines="skip".

    Every physical CSV row is preserved.

    This is especially important for:
        2003-04.csv
        2004-05.csv

    where some rows have an inconsistent number
    of fields.
    """

    encoding = detect_encoding(filepath)

    with open(
        filepath,
        "r",
        encoding=encoding,
        newline=""
    ) as file:

        reader = csv.reader(file)

        rows = list(reader)

    if not rows:

        return [], encoding

    header = rows[0]

    data_rows = rows[1:]

    return (
        [header] + data_rows,
        encoding
    )


def build_season_dataframe(filepath):
    """
    Build a standardized dataframe for one season.
    """

    filename = filepath.name
    season = season_from_filename(filename)

    print()
    print("=" * 75)
    print(f"BUILDING: {filename}")
    print("=" * 75)

    # --------------------------------------------------------
    # Determine relevant columns
    # --------------------------------------------------------

    relevant_columns = get_relevant_columns(
        season
    )

    print(
        f"Season: {season}"
    )

    print(
        f"Relevant columns: "
        f"{len(relevant_columns)}"
    )

    # --------------------------------------------------------
    # Read raw CSV
    # --------------------------------------------------------

    rows, encoding = read_csv_preserve_rows(
        filepath
    )

    if not rows:

        raise ValueError(
            f"Empty CSV file: {filename}"
        )

    header = rows[0]

    header_indexes = {
        column: index
        for index, column
        in enumerate(header)
    }

    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in relevant_columns
        if column not in header_indexes
    ]

    if missing_columns:

        raise ValueError(
            f"Missing relevant columns in "
            f"{filename}: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Extract relevant fields
    # --------------------------------------------------------

    records = []

    for row_number, row in enumerate(
        rows[1:],
        start=2
    ):

        record = {
            "Season": season
        }

        # ----------------------------------------------------
        # Date
        # ----------------------------------------------------

        date_index = header_indexes["Date"]

        raw_date = (
            row[date_index]
            if date_index < len(row)
            else ""
        )

        record["Date"] = parse_date(
            raw_date
        )

        # ----------------------------------------------------
        # Text columns
        # ----------------------------------------------------

        for column in [
            "HomeTeam",
            "AwayTeam",
            "FTR",
            "HTR",
            "Referee",
        ]:

            if column not in relevant_columns:
                continue

            index = header_indexes[column]

            value = (
                row[index]
                if index < len(row)
                else ""
            )

            record[column] = clean_string(
                value
            )

        # ----------------------------------------------------
        # Numeric columns
        # ----------------------------------------------------

        for column in [
            "FTHG",
            "FTAG",
            "HTHG",
            "HTAG",
            "HS",
            "AS",
            "HST",
            "AST",
            "HF",
            "AF",
            "HC",
            "AC",
            "HY",
            "AY",
            "HR",
            "AR",
        ]:

            if column not in relevant_columns:
                continue

            index = header_indexes[column]

            value = (
                row[index]
                if index < len(row)
                else ""
            )

            record[column] = clean_numeric(
                value
            )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        record["_source_file"] = filename
        record["_source_row"] = row_number

        records.append(record)

    df = pd.DataFrame(
        records
    )

    # --------------------------------------------------------
    # Match identification
    # --------------------------------------------------------

    df["_is_match"] = (
        df["Date"].notna()
        & df["HomeTeam"].ne("")
        & df["AwayTeam"].ne("")
    )

    # --------------------------------------------------------
    # Column order
    # --------------------------------------------------------

    final_columns = (
        ["Season"]
        + relevant_columns
        + [
            "_source_file",
            "_source_row",
            "_is_match",
        ]
    )

    df = df[
        final_columns
    ]

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    print(
        f"Raw CSV rows: "
        f"{len(rows) - 1}"
    )

    print(
        f"Rows preserved: "
        f"{len(df)}"
    )

    print(
        f"Match rows: "
        f"{df['_is_match'].sum()}"
    )

    print(
        f"Encoding: "
        f"{encoding}"
    )

    return df


# ============================================================
# BUILD COMPLETE DATASET
# ============================================================

def main():

    print("=" * 75)
    print("PREMIER LEAGUE - BUILD MATCH DATASET")
    print("=" * 75)

    # --------------------------------------------------------
    # Check raw directory
    # --------------------------------------------------------

    if not RAW_DATA_DIR.exists():

        print()
        print(
            "ERROR: Raw data directory does not exist."
        )

        return

    # --------------------------------------------------------
    # Find files
    # --------------------------------------------------------

    csv_files = sorted(
        RAW_DATA_DIR.glob("*.csv")
    )

    print()
    print(
        f"CSV files found: "
        f"{len(csv_files)}"
    )

    if not csv_files:

        print(
            "ERROR: No CSV files found."
        )

        return

    # --------------------------------------------------------
    # Build individual season datasets
    # --------------------------------------------------------

    season_dataframes = []

    for filepath in csv_files:

        try:

            season_df = build_season_dataframe(
                filepath
            )

            season_dataframes.append(
                season_df
            )

        except Exception as exc:

            print()
            print(
                f"ERROR while processing "
                f"{filepath.name}:"
            )

            print(
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            raise

    # --------------------------------------------------------
    # Combine seasons
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("COMBINING SEASONS")
    print("=" * 75)

    matches_df = pd.concat(
        season_dataframes,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Keep actual matches only; do not silently drop bad data
    # --------------------------------------------------------

    non_matches = matches_df.loc[~matches_df["_is_match"]].copy()
    print(f"Non-match source rows excluded: {len(non_matches)}")

    # A row with any core match information but without a valid
    # date and both teams is suspicious: stop instead of losing it.
    suspicious = non_matches[
        non_matches[["HomeTeam", "AwayTeam", "FTR"]]
        .fillna("").ne("").any(axis=1)
        | non_matches[["FTHG", "FTAG"]].notna().any(axis=1)
    ]
    if not suspicious.empty:
        print(suspicious[["Season", "_source_file", "_source_row", "Date", "HomeTeam", "AwayTeam"]].head(20).to_string(index=False))
        raise ValueError(f"Found {len(suspicious)} suspicious non-match rows; output not saved")

    matches_df = matches_df.loc[matches_df["_is_match"]].copy()

    # Check all seasons exist, independently of match count.
    found_seasons = set(matches_df["Season"])
    if found_seasons != EXPECTED_SEASONS:
        raise ValueError(f"Season mismatch. Missing: {sorted(EXPECTED_SEASONS - found_seasons)}; extra: {sorted(found_seasons - EXPECTED_SEASONS)}")

    for season, group in matches_df.groupby("Season"):
        expected = 462 if season in EARLY_SEASONS else 380
        if len(group) != expected:
            raise ValueError(f"{season}: expected {expected} matches, got {len(group)}")
        start_year = int(season[:4])
        dates = group["Date"]
        start_date = pd.Timestamp(start_year, 7, 1)
        end_date = pd.Timestamp(start_year + 1, 6, 30)

        # The 2019/20 season finished on 26 July 2020 due to COVID-19.
        if season == "2019/20":
            end_date = pd.Timestamp(2020, 7, 31)

        invalid_date_rows = group.loc[
            dates.isna() | ~dates.between(start_date, end_date)
        ]
        if not invalid_date_rows.empty:
            print(f"\nInvalid dates in {season} (allowed: {start_date.date()} to {end_date.date()}):")
            print(invalid_date_rows[["_source_file", "_source_row", "Date", "HomeTeam", "AwayTeam"]].head(25).to_string(index=False))
            raise ValueError(f"{season}: missing or out-of-season dates ({len(invalid_date_rows)} rows)")

        if group[["HomeTeam", "AwayTeam", "FTR"]].fillna("").eq("").any().any():
            raise ValueError(f"{season}: missing match text fields")
        if group[["FTHG", "FTAG"]].isna().any().any():
            raise ValueError(f"{season}: missing full-time goals")
        home = pd.to_numeric(group["FTHG"], errors="coerce")
        away = pd.to_numeric(group["FTAG"], errors="coerce")
        if (home.isna() | away.isna() | (home < 0) | (away < 0) | (home % 1 != 0) | (away % 1 != 0)).any():
            raise ValueError(f"{season}: invalid full-time goals")
        expected_result = pd.Series(
            ["H" if h > a else "A" if h < a else "D" for h, a in zip(home, away)],
            index=group.index,
        )
        if not group["FTR"].eq(expected_result).all():
            raise ValueError(f"{season}: full-time result does not match goals")
        if group["HomeTeam"].eq(group["AwayTeam"]).any():
            raise ValueError(f"{season}: home and away team identical")
        if group.duplicated(["HomeTeam", "AwayTeam"]).any():
            raise ValueError(f"{season}: duplicate home/away fixture")
        teams = set(group["HomeTeam"]) | set(group["AwayTeam"])
        expected_teams = 22 if season in EARLY_SEASONS else 20
        if len(teams) != expected_teams:
            raise ValueError(f"{season}: expected {expected_teams} teams, got {len(teams)}")
        if (group["HomeTeam"].value_counts().reindex(sorted(teams), fill_value=0) != expected_teams - 1).any():
            raise ValueError(f"{season}: unexpected home matches per team")
        if (group["AwayTeam"].value_counts().reindex(sorted(teams), fill_value=0) != expected_teams - 1).any():
            raise ValueError(f"{season}: unexpected away matches per team")

    if len(matches_df) != 13166:
        raise ValueError(f"Expected 13166 matches, got {len(matches_df)}")

    matches_df = matches_df.sort_values(
        ["Date", "Season", "HomeTeam", "AwayTeam"],
    ).reset_index(drop=True)

    # MatchID is provisional until team names and ordering are finalized.
    matches_df.insert(0, "MatchID", range(1, len(matches_df) + 1))
    matches_df = matches_df.drop(columns=["_is_match"])

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    matches_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d"
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("DATASET BUILD COMPLETE")
    print("=" * 75)

    print(
        f"Total rows: "
        f"{len(matches_df)}"
    )

    print(
        f"Match rows: "
        f"{len(matches_df)}"
    )

    print(
        f"Columns: "
        f"{len(matches_df.columns)}"
    )

    print()
    print(
        f"Output:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print()
    print(
        "Rows per season:"
    )

    season_summary = (
        matches_df
        .groupby("Season")
        .agg(
            rows=("MatchID", "size"),
            matches=("MatchID", "count"),
        )
        .reset_index()
    )

    print(
        season_summary.to_string(
            index=False
        )
    )

    print()
    print("=" * 75)


if __name__ == "__main__":
    main()