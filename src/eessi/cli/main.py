# license (SPDX): GPL-2.0-only
#
# authors:
# - Kenneth Hoste (Ghent University)
# - Alex Domingo (Vrije Universiteit Brussel)

import typer

from eessi.cli.check import app as check_app
from eessi.cli.help import help_callback, version_callback
from eessi.cli.init import app as init_app
from eessi.cli.install import app as install_app
from eessi.cli.shell import app as shell_app

app = typer.Typer(
    help="User-friendly command line interface to EESSI - https://eessi.io",
    # display help if no arguments given
    no_args_is_help=True,
    # we use custom help option to control its placement
    add_help_option=False,
)

app.add_typer(check_app)
app.add_typer(init_app)
app.add_typer(install_app)
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
