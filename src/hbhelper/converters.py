import pandas as pd

# HomeBank expected format
# date, payment, number, payee, memo, amount, category, tags


def is_s_pankki_format(filename: str) -> bool:
    # Read file to pd.DataFrame
    # S-Pankki gives csv file with delimiter=";", decimal="," and columns:
    # 'Kirjauspäivä', 'Maksupäivä', 'Summa', 'Tapahtumalaji', 'Maksaja', 'Saajan nimi',
    # 'Saajan tilinumero', 'Saajan BIC-tunnus', 'Viitenumero', 'Viesti', 'Arkistointitunnus'
    try:
        df = pd.read_csv(filename, delimiter=";", decimal=",", quotechar="'")
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

    return True


def s_pankki_to_dataframe(filename: str) -> pd.DataFrame:
    # Read file to pd.DataFrame

    # S-Pankki gives csv file with delimiter=";", decimal=",", quotechar="'" and columns:
    # 'Kirjauspäivä', 'Maksupäivä', 'Summa', 'Tapahtumalaji', 'Maksaja', 'Saajan nimi',
    # 'Saajan tilinumero', 'Saajan BIC-tunnus', 'Viitenumero', 'Viesti', 'Arkistointitunnus'
    df = pd.read_csv(filename, delimiter=";", decimal=",", quotechar="'")

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
        raise Exception("Unexpected columns")

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

def is_splitwise_format(filename: str) -> pd.DataFrame:
    # Read file to pd.DataFrame
    # Splitwise gives csv file with delimiter=",", decimal=".",
    # first two rows and the last row containing garbage, and columns:
    # 'Date', 'Description', 'Category', 'Cost', 'Currency', your_name, other_name
    try:
        df = pd.read_csv(filename, delimiter=",", decimal=".", skiprows=2)
        df = df[:-1]
    except pd.errors.ParserError:
        return False

    # Verify that the file is in the correct format
    columns = list(df.columns)
    EXPECTED_COLUMNS = ["Date", "Description", "Category", "Cost", "Currency"]
    if len(columns) != 7 or EXPECTED_COLUMNS != columns[:5]:
        return False
    
    return True


def splitwise_to_dataframe(filename: str) -> pd.DataFrame:
    # Read file to pd.DataFrame
    # Splitwise gives csv file with delimiter=",", decimal=".",
    # first two rows and the last row containing garbage, and columns:
    # 'Date', 'Description', 'Category', 'Cost', 'Currency', your_name, other_name
    df = pd.read_csv(filename, delimiter=",", decimal=".", skiprows=2)
    df = df[:-1]

    # Verify that the file is in the correct format
    columns = list(df.columns)
    EXPECTED_COLUMNS = ["Date", "Description", "Category", "Cost", "Currency"]
    if len(columns) != 7 or EXPECTED_COLUMNS != columns[:5]:
        raise Exception("Unexpected columns")

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
