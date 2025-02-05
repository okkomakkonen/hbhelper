import os
from datetime import datetime

import click

from .converters import NoValidConverterError, convert
from .sankey import create_sankey
from .utils import get_begin_and_end_from_dates


@click.group()
def cli():
    """
    hbhelper: Various HomeBank helpers
    """

    return


@cli.command("convert")
@click.argument(
    "path", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def convert_command(path: str):
    """Convert file to HomeBank CSV format"""

    today = datetime.today().strftime("%Y-%m-%d")

    # TODO: what if file already exists? What if filename does not end in .csv?
    dirname, in_filename = os.path.split(os.path.realpath(path))
    out_filename = f"hbhelper-{today}-{in_filename}"
    out_path = os.path.join(dirname, out_filename)

    try:
        formatter = convert(path, out_path)
    except NoValidConverterError as e:
        click.echo(f"Could not find a valid converter for {in_filename}")
        return

    click.echo(
        f"Converted {in_filename} using {formatter} and wrote to file {out_filename}"
    )

    return


@cli.command("sankey")
@click.argument(
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
@click.argument("dates", nargs=-1, type=str)
@click.option("--ignore", multiple=True)
def sankey_command(filename: str, dates: tuple[str], ignore: tuple[str]):
    """Create a Sankey diagram"""

    begin, end = get_begin_and_end_from_dates(dates)

    sankeymatic_file_path = "hbhelper_sankey_source.txt"

    create_sankey(filename, sankeymatic_file_path, begin, end, ignore)

    click.echo(
        f"Wrote SankeyMATIC diagram inputs to {sankeymatic_file_path}, visit https://sankeymatic.com/build/ to create diagram"
    )

    return
