# license (SPDX): GPL-2.0-only
#
# authors:
# - Kenneth Hoste (Ghent University)
# - Alex Domingo (Vrije Universiteit Brussel)

import click
import typer
from rich import print as rich_print
from typer import rich_utils

import eessi


def version_callback(value: bool):
    """
    Show version and exit early.
    """
    if value:
        rich_print(f"[bold]eessi[/bold] version {eessi.__version__}")
        raise typer.Exit()

def help_callback(ctx: click.Context, param: click.Parameter, value: bool):
    """
    Show default help with rich and exit early.
    """
    # ensures this doesn't run during completion or other early parsing phases
    if not value or ctx.resilient_parsing:
        return

    # print default help with rich
    rich_utils.rich_format_help(obj=ctx.command, ctx=ctx, markup_mode="rich")
    ctx.exit()
