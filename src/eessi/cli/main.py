# license (SPDX): GPL-2.0-only
#
# authors:
# - Kenneth Hoste (Ghent University)
# - Alex Domingo (Vrije Universiteit Brussel)
# - Davide Grassano (CECAM-EPFL)

import typer

from eessi.cli import common_options as copts
from eessi.cli.check import app as check_app
from eessi.cli.init import app as init_app
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
app.add_typer(shell_app)


@app.callback()
def main(
    help: copts.HELP = None,
    version: copts.VERSION = None,
):
    """
    Top level eessi command
    """
    pass


if __name__ == "__main__":
    app()
