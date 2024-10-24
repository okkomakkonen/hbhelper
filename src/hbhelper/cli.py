from datetime import datetime
import os

import click

from .converters import converter_types, Converter


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

    possible_converters: list[Converter] = []

    for converter_type in converter_types:
        converter = converter_type(filename)
        if converter.parse():
            possible_converters.append(converter)

    if len(possible_converters) != 1:
        click.echo("Could not figure out file format")
        return 1

    converter = possible_converters[0]

    df = converter.convert()

    today = datetime.today().strftime("%Y-%m-%d")

    df.loc[:, "tags"] += f"hbhelper-{today} "

    dirname = os.path.dirname(os.path.realpath(filename))

    # TODO: fix this
    out_filename = f"hbhelper-{today}-{filename}"
    out_path = os.path.join(dirname, out_filename)

    df.to_csv(out_path, sep=";", index=False)

    click.echo(
        f"Converted {filename} using {converter.name} and wrote to file {out_filename}"
    )

    return 0
