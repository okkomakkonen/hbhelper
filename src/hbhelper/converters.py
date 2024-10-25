"""
This file constructs converters to convert data from a bank or other institution
to the format read by HomeBank.

HomeBank expects a semicolon separated CSV file with the columns
    [date, payment, number, payee, memo, amount, category, tags]
"""

from collections.abc import Callable

import pandas as pd


def s_pankki_converter(filename: str) -> pd.DataFrame | None:
    """
    Convert CSV file from S-Pankki to HomeBank format.

    S-Pankki gives csv file with delimiter=";", decimal=",", quotechar="'" and columns:
        'Kirjauspäivä', 'Maksupäivä', 'Summa', 'Tapahtumalaji', 'Maksaja', 'Saajan nimi',
        'Saajan tilinumero', 'Saajan BIC-tunnus', 'Viitenumero', 'Viesti', 'Arkistointitunnus'
    """

    # Read file to pd.DataFrame
    try:
        df = pd.read_csv(filename, delimiter=";", decimal=",", quotechar="'")
    except pd.errors.ParserError:
        return None

    # Verify that the file is in the correct format
    EXPECTED_COLUMNS = [
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

    # Read file to pd.DataFrame
    try:
        df = pd.read_csv(filename, delimiter=",", decimal=".", skiprows=2)
        df = df[:-1]
    except pd.errors.ParserError:
        return None

    # Verify that the file is in the correct format
    columns = list(df.columns)
    EXPECTED_COLUMNS = ["Date", "Description", "Category", "Cost", "Currency"]
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
    "s-pankki": s_pankki_converter,
    "splitwise": splitwise_converter,
}
