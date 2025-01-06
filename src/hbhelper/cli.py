import click

from .converters import convert


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

