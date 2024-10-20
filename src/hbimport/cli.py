import click

from .importers import s_pankki_to_dataframe, splitwise_to_dataframe

from datetime import datetime


@click.group()
def cli():
    """
    hbimporter: import files to homebank csv format
    """

    return


@cli.command("s-pankki")
@click.argument(
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def s_pankki_command(filename: str):
    """Import from S-Pankki"""

    click.echo(f"Transforming {filename} to Homebank CSV format")

    df = s_pankki_to_dataframe(filename)

    today = datetime.today()

    # 2024-10-20-hbimport-s-pankki.csv
    filename = today.strftime("%Y-%m-%d") + "-hbimport-s-pankki.csv"

    df.to_csv(filename, sep=";", index=False)

    click.echo(f"Wrote final CSV to {filename}")

    return


@cli.command("splitwise")
@click.argument(
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def splitwise_command(filename: str):
    """Import from Splitwise"""

    click.echo(f"Transforming {filename} to Homebank CSV format")

    df = splitwise_to_dataframe(filename)

    today = datetime.today()

    # 2024-10-20-hbimport-splitwise.csv
    filename = today.strftime("%Y-%m-%d") + "-hbimport-splitwise.csv"

    df.to_csv(filename, sep=";", index=False)

    click.echo(f"Wrote final CSV to {filename}")

    return
