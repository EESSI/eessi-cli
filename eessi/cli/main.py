# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import typer
import sys

from eessi.cli.check import app as check_app
from eessi.cli.init import app as init_app
from eessi.cli.shell import app as shell_app

app = typer.Typer(help="User-friendly command line interface to EESSI - https://eessi.io")

app.add_typer(check_app)
app.add_typer(init_app)
app.add_typer(shell_app)


if __name__ == "__main__":
    app()
