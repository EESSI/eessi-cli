# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import typer

import eessi
from eessi.cli.check import app as check_app
from eessi.cli.init import app as init_app
from eessi.cli.shell import app as shell_app

app = typer.Typer(
    help="User-friendly command line interface to EESSI - https://eessi.io",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)

app.add_typer(check_app)
app.add_typer(init_app)
app.add_typer(shell_app)

def version_callback(value: bool):
    if value:
        print(f"eessi version {eessi.__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,  # default value
        "-v",  # short option
        "--version",  # long option
        help="Show version of eessi CLI",
        callback=version_callback,
    ),
):
    pass


if __name__ == "__main__":
    app()
