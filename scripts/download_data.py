from pathlib import Path
import requests
import time


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# SEASON CONFIGURATION
# ============================================================

START_YEAR = 1993
END_YEAR = 2025


# ============================================================
# SOURCE CONFIGURATION
# ============================================================

BASE_URL = (
    "https://www.football-data.co.uk/"
    "mmz4281"
)

DIVISION = "E0"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_season_label(start_year):
    """
    Creates a project season label.

    Example:
    1993 -> 1993-94
    2024 -> 2024-25
    """

    end_year_short = (start_year + 1) % 100

    return f"{start_year}-{end_year_short:02d}"


def create_source_season_code(start_year):
    """
    Creates the season code used by Football-Data.

    Example:
    1993 -> 9394
    2024 -> 2425
    """

    return (
        f"{str(start_year)[-2:]}"
        f"{str(start_year + 1)[-2:]}"
    )


def create_download_url(start_year):
    """
    Creates the complete download URL
    for one Premier League season.
    """

    season_code = create_source_season_code(start_year)

    return (
        f"{BASE_URL}/"
        f"{season_code}/"
        f"{DIVISION}.csv"
    )


def download_season(start_year):
    """
    Downloads one Premier League season.
    """

    season_label = create_season_label(start_year)

    url = create_download_url(start_year)

    output_file = RAW_DATA_DIR / f"{season_label}.csv"

    print("=" * 60)
    print(f"Season: {start_year}/{start_year + 1}")
    print(f"URL: {url}")
    print(f"Output: {output_file}")

    # Do not download the file again if it already exists.
    if output_file.exists():

        print("Status: file already exists - skipped")

        return "skipped"

    try:

        response = requests.get(
            url,
            timeout=30
        )

        print(
            f"HTTP status code: "
            f"{response.status_code}"
        )

        if response.status_code == 200:

            output_file.write_bytes(
                response.content
            )

            print(
                "Status: downloaded successfully"
            )

            return "downloaded"

        else:

            print(
                "Status: download failed"
            )

            return "failed"

    except requests.RequestException as error:

        print(
            f"Status: request error - {error}"
        )

        return "failed"


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    # Create the raw data directory if necessary.
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 60)
    print("PREMIER LEAGUE DATA DOWNLOAD")
    print("=" * 60)

    print(
        f"Project root: "
        f"{PROJECT_ROOT}"
    )

    print(
        f"Raw data directory: "
        f"{RAW_DATA_DIR}"
    )

    print(
        f"Downloading seasons from "
        f"{START_YEAR}/{START_YEAR + 1} "
        f"to "
        f"{END_YEAR}/{END_YEAR + 1}"
    )

    print()

    downloaded = 0
    skipped = 0
    failed = 0

    for start_year in range(
        START_YEAR,
        END_YEAR + 1
    ):

        result = download_season(
            start_year
        )

        if result == "downloaded":

            downloaded += 1

        elif result == "skipped":

            skipped += 1

        elif result == "failed":

            failed += 1

        # Small pause between requests.
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)

    print(f"Downloaded: {downloaded}")
    print(f"Skipped:    {skipped}")
    print(f"Failed:     {failed}")

    print("=" * 60)


if __name__ == "__main__":
    main()