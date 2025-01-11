import click

from .converters import convert
from .sankey import create_sankey


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
@click.argument("year", type=int)
@click.option("--ignore", multiple=True)
def sankey_command(filename: str, year: int, ignore: tuple[str]):
    """Create a Sankey diagram"""

    message = create_sankey(filename, year, ignore)

    click.echo(message)

    return
