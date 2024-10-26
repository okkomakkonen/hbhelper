import os
from datetime import datetime

import click

from .converters import converters, validate_dataframe


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

    # Parse file with first converter that accepts it
    for format, converter in converters.items():
        # Try to parse file using the converter
        df = converter(filename)

        if df is not None:
            break
    else:
        click.echo(f"Could not find a valid converter for {filename}")
        return

    # Validate dataframe
    assert validate_dataframe(df)

    # Add a tag to each entry
    today = datetime.today().strftime("%Y-%m-%d")
    df.loc[:, "tags"] += f"hbhelper-{today} "

    # TODO: what if file already exists? what if filename does not end in .csv
    dirname = os.path.dirname(os.path.realpath(filename))
    out_filename = f"hbhelper-{today}-{filename}"
    out_path = os.path.join(dirname, out_filename)

    # Write dataframe to file
    df.to_csv(out_path, sep=";", index=False)

    click.echo(f"Converted {filename} using {format} and wrote to file {out_filename}")

    return
