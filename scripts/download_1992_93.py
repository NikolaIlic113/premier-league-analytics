from pathlib import Path
import re
import requests
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

URL = "https://www.rsssf.org/tablese/eng93.html"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "1992-93.csv"


# ============================================================
# TEAM NAME STANDARDIZATION
# ============================================================

TEAM_NAMES = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Blackburn Rovers": "Blackburn",
    "Chelsea": "Chelsea",
    "Coventry City": "Coventry",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Ipswich Town": "Ipswich",
    "Leeds United": "Leeds",
    "Liverpool": "Liverpool",
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Middlesbrough": "Middlesbrough",
    "Norwich City": "Norwich",
    "Nottingham Forest": "Nott'm Forest",
    "Oldham Athletic": "Oldham",
    "Queens Park Rangers": "QPR",
    "Sheffield United": "Sheffield United",
    "Sheffield Wednesday": "Sheffield Wednesday",
    "Southampton": "Southampton",
    "Tottenham Hotspur": "Tottenham",
    "Wimbledon": "Wimbledon",
}


# ============================================================
# DOWNLOAD SOURCE
# ============================================================

def download_source():
    print("=" * 70)
    print("DOWNLOADING 1992-93 PREMIER LEAGUE DATA")
    print("=" * 70)

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    print(f"HTTP status: {response.status_code}")
    print(f"Downloaded bytes: {len(response.content):,}")

    return response.text


# ============================================================
# EXTRACT MATCHES
# ============================================================

def extract_matches(html):
    """
    Extract matches from the RSSSF 1992/93 page.

    Expected format in the source:

        15 August 1992
        Arsenal                     2    Norwich City                4

    We extract:
        Date
        HomeTeam
        AwayTeam
        FTHG
        FTAG
    """

    # Convert HTML to plain text while preserving line structure.
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML entities.
    import html as html_module
    text = html_module.unescape(text)

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    matches = []

    current_date = None

    # Example:
    # 15 August 1992
    date_pattern = re.compile(
        r"^\d{1,2}\s+"
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}$"
    )

    # Match pattern:
    #
    # Arsenal  2  Norwich City  4
    #
    # The source uses whitespace alignment rather than commas.
    #
    # We therefore identify rows containing two integer scores
    # and use the known team names to determine the split.

    known_teams = sorted(
        TEAM_NAMES.keys(),
        key=len,
        reverse=True
    )

    for line in lines:

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        if date_pattern.match(line):
            current_date = line
            continue

        if current_date is None:
            continue

        # ----------------------------------------------------
        # MATCH
        # ----------------------------------------------------

        # Try every known home team.
        found = False

        for home_team in known_teams:

            if not line.startswith(home_team):
                continue

            remainder = line[len(home_team):].strip()

            # Home score
            score_match = re.match(r"^(\d+)\s+", remainder)

            if not score_match:
                continue

            home_goals = int(score_match.group(1))
            remainder = remainder[score_match.end():].strip()

            # Try every possible away team.
            for away_team in known_teams:

                if not remainder.startswith(away_team):
                    continue

                remainder_after_team = (
                    remainder[len(away_team):].strip()
                )

                away_score_match = re.match(
                    r"^(\d+)(?:\s|$)",
                    remainder_after_team
                )

                if not away_score_match:
                    continue

                away_goals = int(
                    away_score_match.group(1)
                )

                matches.append(
                    {
                        "Date": current_date,
                        "HomeTeam": TEAM_NAMES[home_team],
                        "AwayTeam": TEAM_NAMES[away_team],
                        "FTHG": home_goals,
                        "FTAG": away_goals,
                    }
                )

                found = True
                break

            if found:
                break

    return matches


# ============================================================
# CREATE DATAFRAME
# ============================================================

def create_dataframe(matches):

    df = pd.DataFrame(matches)

    if df.empty:
        raise ValueError(
            "No matches were extracted from the source."
        )

    # Parse dates.
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d %B %Y"
    )

    # Full-time result.
    df["FTR"] = df.apply(
        lambda row:
            "H"
            if row["FTHG"] > row["FTAG"]
            else "A"
            if row["FTHG"] < row["FTAG"]
            else "D",
        axis=1
    )

    # Put columns in the same conceptual order as
    # Football-Data.
    df = df[
        [
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG",
            "FTR",
        ]
    ]

    return df


# ============================================================
# VALIDATION
# ============================================================

def validate_1992_93(df):

    print()
    print("=" * 70)
    print("1992-93 BASIC VALIDATION")
    print("=" * 70)

    expected_matches = 462
    expected_teams = 22
    expected_matches_per_team = 42

    print(f"Rows: {len(df)}")
    print(f"Unique teams: {len(set(df['HomeTeam']) | set(df['AwayTeam']))}")

    print()
    print("Date range:")
    print(f"First match: {df['Date'].min().date()}")
    print(f"Last match:  {df['Date'].max().date()}")

    print()
    print("Missing values:")
    print(df.isna().sum())

    print()
    print("Negative goals:")
    print(
        "Home:",
        (df["FTHG"] < 0).sum()
    )
    print(
        "Away:",
        (df["FTAG"] < 0).sum()
    )

    print()
    print("Invalid results:")
    print(
        (~df["FTR"].isin(["H", "D", "A"])).sum()
    )

    print()
    print("Duplicate matches:")
    print(
        df.duplicated(
            subset=[
                "Date",
                "HomeTeam",
                "AwayTeam"
            ]
        ).sum()
    )

    # --------------------------------------------------------
    # MATCHES PER TEAM
    # --------------------------------------------------------

    home_counts = df["HomeTeam"].value_counts()
    away_counts = df["AwayTeam"].value_counts()

    teams = sorted(
        set(df["HomeTeam"]) |
        set(df["AwayTeam"])
    )

    team_validation = pd.DataFrame(
        {
            "HomeMatches": home_counts,
            "AwayMatches": away_counts,
        }
    ).fillna(0)

    team_validation["TotalMatches"] = (
        team_validation["HomeMatches"] +
        team_validation["AwayMatches"]
    )

    print()
    print("Matches per team:")
    print(team_validation.sort_index())

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    checks = {
        "match_count": len(df) == expected_matches,
        "team_count": len(teams) == expected_teams,
        "matches_per_team": (
            team_validation["TotalMatches"] ==
            expected_matches_per_team
        ).all(),
        "no_missing": not df.isna().any().any(),
        "no_negative_goals": (
            (df["FTHG"] >= 0).all()
            and
            (df["FTAG"] >= 0).all()
        ),
        "valid_results": df["FTR"].isin(
            ["H", "D", "A"]
        ).all(),
        "no_duplicates": (
            df.duplicated(
                subset=[
                    "Date",
                    "HomeTeam",
                    "AwayTeam"
                ]
            ).sum() == 0
        ),
    }

    print()
    print("Validation checks:")

    for check, passed in checks.items():
        print(
            f"  {'PASS' if passed else 'FAIL'} - {check}"
        )

    print()

    if all(checks.values()):
        print("STATUS: 1992-93 validation PASSED.")
    else:
        print("STATUS: 1992-93 validation FAILED.")

    print("=" * 70)

    return checks


# ============================================================
# MAIN
# ============================================================

def main():

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    html = download_source()

    matches = extract_matches(html)

    print()
    print(f"Extracted matches: {len(matches)}")

    df = create_dataframe(matches)

    validate_1992_93(df)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print()
    print(f"Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()