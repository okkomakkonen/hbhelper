import click

from .converters import convert
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
    "filename", nargs=1, type=click.Path(exists=True, readable=True, dir_okay=False)
)
def convert_command(filename: str):
    """Convert file to HomeBank CSV format"""

    message = convert(filename)

    click.echo(message)

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

    message = create_sankey(filename, begin, end, ignore)

    click.echo(message)

    return
