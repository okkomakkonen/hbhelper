"""
This file constructs converters to convert data from a bank or other institution
to the format read by HomeBank.

HomeBank expects a semicolon separated CSV file with the columns
    [date, payment, number, payee, memo, amount, category, tags]
"""

import pandas as pd


class Converter:
    name = "default"

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._df: pd.DataFrame | None = None

    def parse(self) -> bool:
        return NotImplemented

    def convert(self) -> pd.DataFrame:
        return NotImplemented


class SPankkiConverter(Converter):
    name = "s-pankki"

    def parse(self) -> bool:
        # Read file to pd.DataFrame
        # S-Pankki gives csv file with delimiter=";", decimal=",", quotechar="'" and columns:
        # 'Kirjauspäivä', 'Maksupäivä', 'Summa', 'Tapahtumalaji', 'Maksaja', 'Saajan nimi',
        # 'Saajan tilinumero', 'Saajan BIC-tunnus', 'Viitenumero', 'Viesti', 'Arkistointitunnus'
        try:
            df = pd.read_csv(self._filename, delimiter=";", decimal=",", quotechar="'")
        except pd.errors.ParserError:
            return False

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
        if len(columns) != 11 or EXPECTED_COLUMNS != columns:
            return False

        self._df = df

        return True

    def convert(self) -> pd.DataFrame:
        df = self._df

        if df is None:
            raise Exception("incorrect format")

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


class SplitwiseConverter(Converter):
    name = "splitwise"

    def parse(self) -> bool:
        # Read file to pd.DataFrame
        # Splitwise gives csv file with delimiter=",", decimal=".",
        # first two rows and the last row containing garbage, and columns:
        # 'Date', 'Description', 'Category', 'Cost', 'Currency', your_name, other_name
        try:
            df = pd.read_csv(self._filename, delimiter=",", decimal=".", skiprows=2)
            df = df[:-1]
        except pd.errors.ParserError:
            return False

        # Verify that the file is in the correct format
        columns = list(df.columns)
        EXPECTED_COLUMNS = ["Date", "Description", "Category", "Cost", "Currency"]
        if len(columns) != 7 or EXPECTED_COLUMNS != columns[:5]:
            return False

        self._df = df

        return True

    def convert(self) -> pd.DataFrame:
        df = self._df

        if df is None:
            raise Exception("incorrect format")

        # The column your_name contains the amount for you
        # TODO: this is wrong, the columns are in alphabetical order
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


converter_types = [SPankkiConverter, SplitwiseConverter]
