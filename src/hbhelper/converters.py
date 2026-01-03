"""
This file constructs converters to convert data from a bank or other institution
to the format read by HomeBank.

HomeBank expects a semicolon separated CSV file with the columns
    [date, payment, number, payee, memo, amount, category, tags]
"""

from collections.abc import Callable
from datetime import datetime
from typing import Final

import pandas as pd


class NoValidConverterError(Exception):
    pass


def convert(in_path: str, out_path: str) -> str:
    """Convert file to HomeBank CSV format

    Returns the name of the converter that was used
    """

    # Parse file with first converter that accepts it
    for formatter, converter in converters.items():
        # Try to parse file using the converter
        df = converter(in_path)

        if df is not None:
            break
    else:
        raise NoValidConverterError("Could not find a valid converter")

    # Validate dataframe
    assert validate_dataframe(df)

    # Add a tag to each entry
    today = datetime.today().strftime("%Y-%m-%d")
    df.loc[:, "tags"] += f"hbhelper-{today} "

    # Write dataframe to file
    df.to_csv(out_path, sep=";", index=False)

    return formatter


def validate_dataframe(df: pd.DataFrame) -> bool:
    """Validate that the given dataframe is in the correct format for HomeBank."""
    EXPECTED_COLUMNS: Final = [
        "date",
        "payment",
        "number",
        "payee",
        "memo",
        "amount",
        "category",
        "tags",
    ]

    return list(df.columns) == EXPECTED_COLUMNS


def nordea_converter(filename: str) -> pd.DataFrame | None:
    """
    Convert CSV file from Nordea to HomeBank format.

    Nordea gives csv file with delimiter=";", decimal="," and columns:
        'Kirjauspäivä', 'Määrä', 'Maksaja', 'Maksunsaaja', 'Nimi', 'Otsikko',
        'Viitenumero', 'Saldo', 'Valuutta', 'Unnamed: 9'
    """

    if not filename.endswith(".csv"):
        return None

    # Read file to pd.DataFrame
    try:
        df = pd.read_csv(filename, delimiter=";", decimal=",")
    except pd.errors.ParserError:
        return None

    columns = list(df.columns)

    EXPECTED_COLUMNS_v1: Final = [
        "Kirjauspäivä",
        "Määrä",
        "Maksaja",
        "Maksunsaaja",
        "Nimi",
        "Otsikko",
        "Viitenumero",
        "Saldo",
        "Valuutta",
        "Unnamed: 9",
    ]

    if columns == EXPECTED_COLUMNS_v1:
        # Remove some rows
        df = df.loc[df["Kirjauspäivä"] != "Varaus"]

        # Add new columns
        df["date"] = pd.to_datetime(df["Kirjauspäivä"], format="%Y/%m/%d")
        df["payment"] = ""
        df["number"] = ""
        df["payee"] = df["Otsikko"]
        df["memo"] = ""
        df["amount"] = df["Määrä"]
        df["category"] = ""
        df["tags"] = ""

        # Remove unnecessary columns
        df = df[
            ["date", "payment", "number", "payee", "memo", "amount", "category", "tags"]
        ]

        return df

    EXPECTED_COLUMNS_v2: Final = [
        "Kirjauspäivä",
        "Määrä",
        "Maksaja",
        "Maksunsaaja",
        "Nimi",
        "Otsikko",
        "Viesti",
        "Viitenumero",
        "Saldo",
        "Valuutta",
        "Unnamed: 10",
    ]

    if columns == EXPECTED_COLUMNS_v2:
        # Remove some rows
        df = df.loc[df["Kirjauspäivä"] != "Varaus"]

        # Add new columns
        df["date"] = pd.to_datetime(df["Kirjauspäivä"], format="%Y/%m/%d")
        df["payment"] = ""
        df["number"] = ""
        df["payee"] = df["Otsikko"]
        df["memo"] = ""
        df["amount"] = df["Määrä"]
        df["category"] = ""
        df["tags"] = ""

        # Remove unnecessary columns
        df = df[
            ["date", "payment", "number", "payee", "memo", "amount", "category", "tags"]
        ]

        return df

    return None


def s_pankki_converter(filename: str) -> pd.DataFrame | None:
    """
    Convert CSV file from S-Pankki to HomeBank format.

    S-Pankki gives csv file with delimiter=";", decimal=",", quotechar="'" and columns:
        'Kirjauspäivä', 'Maksupäivä', 'Summa', 'Tapahtumalaji', 'Maksaja', 'Saajan nimi',
        'Saajan tilinumero', 'Saajan BIC-tunnus', 'Viitenumero', 'Viesti', 'Arkistointitunnus'
    """

    if not filename.endswith(".csv"):
        return None

    # Read file to pd.DataFrame
    try:
        df = pd.read_csv(filename, delimiter=";", decimal=",", quotechar="'")
    except pd.errors.ParserError:
        return None

    # Verify that the file is in the correct format
    EXPECTED_COLUMNS: Final = [
        "Kirjauspäivä",
        "Maksupäivä",
        "Summa",
        "Tapahtumalaji",
        "Maksaja",
        "Saajan nimi",
        "Saajan tilinumero",
        "Saajan BIC-tunnus",
        "Viitenumero",
        "Viesti",
        "Arkistointitunnus",
    ]
    columns = list(df.columns)
    if len(columns) != 11 or columns != EXPECTED_COLUMNS:
        return None

    # Do some processing on the data
    df.loc[df["Tapahtumalaji"] == "KORTTIOSTO", "Viesti"] = ""
    df.loc[df["Viesti"] == "-", "Viesti"] = ""

    # Add new columns
    df["date"] = pd.to_datetime(df["Maksupäivä"], format="%d.%m.%Y")
    df["payment"] = ""
    df["number"] = ""
    df["payee"] = ""
    df["memo"] = df["Viesti"]
    df["amount"] = df["Summa"]
    df["category"] = ""
    df["tags"] = ""

    # Add payee depending on the sign of the transaction
    df.loc[df["Summa"] > 0, "payee"] = df["Maksaja"]
    df.loc[df["Summa"] <= 0, "payee"] = df["Saajan nimi"]

    # Remove unnecessary columns
    df = df[
        ["date", "payment", "number", "payee", "memo", "amount", "category", "tags"]
    ]

    return df


def splitwise_converter(filename: str) -> pd.DataFrame | None:
    """
    Convert CSV file from Splitwise to HomeBank format.

    Splitwise gives csv file with delimiter=",", decimal=".", first two rows and the last row containing garbage, and columns:
        'Date', 'Description', 'Category', 'Cost', 'Currency', your_name, other_name
    """

    if not filename.endswith(".csv"):
        return None

    # Read file to pd.DataFrame
    try:
        df = pd.read_csv(filename, delimiter=",", decimal=".", skiprows=2)
        df = df[:-1]
    except pd.errors.ParserError:
        return None

    # Verify that the file is in the correct format
    columns = list(df.columns)
    EXPECTED_COLUMNS: Final = ["Date", "Description", "Category", "Cost", "Currency"]
    if len(columns) != 7 or columns[:5] != EXPECTED_COLUMNS:
        return None

    # The column your_name contains the amount for you
    # NOTE: this is wrong, the columns are in alphabetical order
    your_name = df.columns[-2]
    other_name = df.columns[-1]

    # Add new columns
    df["date"] = pd.to_datetime(df["Date"])
    df["payment"] = ""
    df["number"] = ""
    df["payee"] = other_name
    df["memo"] = df["Description"]
    df["amount"] = df[your_name]
    df["category"] = ""
    df["tags"] = ""

    # Remove unnecessary columns
    df = df[
        ["date", "payment", "number", "payee", "memo", "amount", "category", "tags"]
    ]

    return df


# These are the converters available
converters: dict[str, Callable[[str], pd.DataFrame | None]] = {
    "nordea": nordea_converter,
    "s-pankki": s_pankki_converter,
    "splitwise": splitwise_converter,
}
