from datetime import datetime
import os

import click

from .converters import s_pankki_to_dataframe, splitwise_to_dataframe, is_s_pankki_format, is_splitwise_format


@click.group()
def cli():
    """
    hbhelper: Various HomeBank helpers
    """

    return


@cli.command("convert")
@click.argument(
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def convert_command(filename: str):
    """Convert file to HomeBank CSV format"""

    possible_formats: list[str] = []

    if is_s_pankki_format(filename):
        possible_formats.append("S-Pankki")
    
    if is_splitwise_format(filename):
        possible_formats.append("Splitwise")

    if len(possible_formats) != 1:
        click.echo("Could not figure out file format")
        return 1

    format = possible_formats[0]

    if format == "S-Pankki":
        df = s_pankki_to_dataframe(filename)
    elif format == "Splitwise":
        df = splitwise_to_dataframe(filename)
    else:
        return 1

    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")

    df["tags"] += f" hbhelper-{today_str}"

    dirname = os.path.dirname(os.path.realpath(filename))

    out_filename = os.path.join(dirname, f"hbhelper-{today_str}-{filename}")

    df.to_csv(out_filename, sep=";", index=False)

    click.echo(f"Converted {filename} using {format} and wrote to file {out_filename}")

    return 0


@cli.command("s-pankki")
@click.argument(
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def s_pankki_command(filename: str):
    """Import from S-Pankki (DEPRECATED)"""

    click.echo(f"Transforming {filename} to Homebank CSV format")

    df = s_pankki_to_dataframe(filename)

    today = datetime.today()

    # 2024-10-20-hbhelper-s-pankki.csv
    filename = today.strftime("%Y-%m-%d") + "-hbhelper-s-pankki.csv"

    df.to_csv(filename, sep=";", index=False)

    click.echo(f"Wrote final CSV to {filename}")

    return


@cli.command("splitwise")
@click.argument(
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def splitwise_command(filename: str):
    """Import from Splitwise (DEPRECATED)"""

    click.echo(f"Transforming {filename} to Homebank CSV format")

    df = splitwise_to_dataframe(filename)

    today = datetime.today()

    # 2024-10-20-hbhelper-splitwise.csv
    filename = today.strftime("%Y-%m-%d") + "-hbhelper-splitwise.csv"

    df.to_csv(filename, sep=";", index=False)

    click.echo(f"Wrote final CSV to {filename}")

    return
