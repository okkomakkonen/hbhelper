from datetime import datetime

import click

from .converters import s_pankki_to_dataframe, splitwise_to_dataframe


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

    # TODO: figure out what format(s) the file is in (what to do if there are multiple options)
    format = ...
    # TODO: convert using that backend
    df = ...

    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")

    df["tags"] += f" hbhelper-{today_str}"

    # TODO: find directory of original file and write to the same folder

    out_filename = ...

    # TODO: write to file (what to do if file already exists)

    click.echo(f"Converted {filename} using {format} and wrote to file {out_filename}")

    return


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
