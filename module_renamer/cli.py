# -*- coding: utf-8 -*-
"""Console script for module_renamer."""
from __future__ import absolute_import

import sys

import click

from .commands.analyze_modifications import analyze_modifications

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    Console script for module_renamer.
    """
    pass


@main.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--compare-with', default='master',
              help='Branch to be compared with [Default: master]')
@click.option('--branch', default=False,
              help='Branch that has the modifications [Default: current active branch]')
@click.option('--output-file', default='list_output.py',
              help='Change the name of the output file [Default: list_output.py]')
def analyze(project_path, compare_with, branch, output_file):
    """
    Generate the difference between the imports on two different branches.

    Command to analyze all modifications made between two different branches. The output will be a
    list written directly to a file (which will later be used by the script to rename the imports)

    Ex.:
    The following command generate a "list_output.py" with the difference between the
    current branch (that contains the modification) against the master.

    > renamer analyze project_path

    It's possible to use the flag --branch to point to branch different than the current one.
    It's possible to set --output-file to change the default output file name.

    > renamer analyze project_path --branch=my-branch --output-file=my_file.py

    And finally, it's possible to change the branch with which the modifications will be compared.

    > renamer analyze project_path --branch=my-branch --compare-with=my-other-branch

    """
    analyze_modifications(project_path, compare_with, branch, output_file)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
