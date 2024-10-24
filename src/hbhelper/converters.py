import pandas as pd

# HomeBank expected format
# date, payment, number, payee, memo, amount, category, tags


def s_pankki_to_dataframe(filename: str) -> pd.DataFrame:
    # Read file to pd.DataFrame
    # S-Pankki gives csv file with delimiter=";", decimal="," and columns:
    # 'Kirjauspäivä', 'Maksupäivä', 'Summa', 'Tapahtumalaji', 'Maksaja', 'Saajan nimi',
    # 'Saajan tilinumero', 'Saajan BIC-tunnus', 'Viitenumero', 'Viesti', 'Arkistointitunnus'
    df = pd.read_csv(filename, delimiter=";", decimal=",")

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

    # Remove unnecessary data
    df.loc[df["Tapahtumalaji"] == "KORTTIOSTO", "Viesti"] = ""
    df["Tapahtumalaji"] = ""

    # Rename columns
    df.rename(
        columns={
            "Maksupäivä": "date",
            "Summa": "amount",
            "Saajan nimi": "payee",
            "Viesti": "memo",
            "Tapahtumalaji": "payment",
        },
        inplace=True,
    )

    # Add new columns
    df["tags"] = ""
    df["number"] = ""
    df["category"] = ""

    # Remove unnecessary columns
    df = df[
        ["date", "payment", "number", "payee", "memo", "amount", "category", "tags"]
    ]

    # Change date to a datetime object
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")

    return df


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
    your_name = df.columns[-2]

    # Rename columns
    df.rename(
        columns={your_name: "amount", "Description": "memo", "Date": "date"},
        inplace=True,
    )

    # Add new columns
    df["tags"] = ""
    df["number"] = ""
    df["category"] = ""
    df["payment"] = ""
    df["payee"] = ""

    # Remove unnecessary columns
    df = df[
        ["date", "payment", "number", "payee", "memo", "amount", "category", "tags"]
    ]

    # Change date to a datetime object
    df["date"] = pd.to_datetime(df["date"])

    return df
