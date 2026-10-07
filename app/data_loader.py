from pathlib import Path
from io import StringIO

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_csv(file_name: str) -> pd.DataFrame:
    """
    Load one of the company's CSV files.

    The provided CSV files contain each complete row inside
    double quotes, so we normalize the raw content before
    passing it to pandas.

    keep_default_na=False is used so that legitimate values
    such as "NA" remain as strings instead of being converted
    into pandas NaN values.
    """

    file_path = DATA_DIR / file_name

    # --------------------------------------------------
    # 1. Read raw file
    # --------------------------------------------------

    raw_text = file_path.read_text(
        encoding="utf-8-sig"
    )

    # --------------------------------------------------
    # 2. Remove outer quotes from each line
    # --------------------------------------------------

    cleaned_lines = []

    for line in raw_text.splitlines():

        line = line.strip()

        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]

        cleaned_lines.append(line)

    # --------------------------------------------------
    # 3. Reconstruct a normal CSV
    # --------------------------------------------------

    cleaned_csv = "\n".join(
        cleaned_lines
    )

    # --------------------------------------------------
    # 4. Parse CSV
    # --------------------------------------------------

    df = pd.read_csv(
        StringIO(cleaned_csv),
        keep_default_na=False
    )

    return df


def load_sales_data() -> pd.DataFrame:
    """
    Load sales data.
    """

    return load_csv(
        "sales_data.csv"
    )


def load_targets_data() -> pd.DataFrame:
    """
    Load target data.
    """

    return load_csv(
        "targets.csv"
    )