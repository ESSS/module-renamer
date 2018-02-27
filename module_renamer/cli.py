# -*- coding: utf-8 -*-
"""Console script for module_renamer."""
from __future__ import absolute_import

import sys

import click

from .commands.track_modifications import track_modifications

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    Console script for module_renamer.
    """
    pass


@main.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--origin_branch', default='master',
              help='Branch to start the evaluation')
@click.option('--work_branch', default=False,
              help='Name of the branch that has the modifications')
@click.option('--output_file', default='list_output.py',
              help='Change the name of the output file')
def track(**kwargs):
    track_modifications(**kwargs)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
