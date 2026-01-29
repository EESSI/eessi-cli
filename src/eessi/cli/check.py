# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import typer

from eessi.cli.help import help_callback

app = typer.Typer()


@app.command()
def check(
    help: bool = typer.Option(
        None,  # default value
        "-h",
        "--help",
        help="Show this message and exit.",
        callback=help_callback,
        is_eager=True,
    ),
):
    """
    Check CernVM-FS setup for accessing EESSI
    """
    raise NotImplementedError
