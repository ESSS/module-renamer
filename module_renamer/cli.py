# -*- coding: utf-8 -*-

"""Console script for module_renamer."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for module_renamer."""
    click.echo("Replace this message by putting your code into "
               "module_renamer.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
