# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import click
import typer
from rich import print as rich_print
from typer import rich_utils

import eessi
from eessi.cli.check import app as check_app
from eessi.cli.init import app as init_app
from eessi.cli.shell import app as shell_app


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

app = typer.Typer(
    help="User-friendly command line interface to EESSI - https://eessi.io",
    # display help if no arguments given
    no_args_is_help=True,
    # we use custom help option to control its placement
    add_help_option=False,
)

app.add_typer(check_app)
app.add_typer(init_app)
app.add_typer(shell_app)


@app.callback()
def main(
    help: bool = typer.Option(
        None,  # default value
        "-h",
        "--help",
        help="Show this message and exit.",
        callback=help_callback,
        is_eager=True,
    ),
    version: bool = typer.Option(
        None,  # default value
        "-v",
        "--version",
        help="Show version of eessi CLI.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    Top level eessi command
    """
    pass


if __name__ == "__main__":
    app()
