# license (SPDX): GPL-2.0-only
#
# authors:
# - Alex Domingo (Vrije Universiteit Brussel)

import sys
import typing as t

import typer
from rich import print as rich_print


def report_error(msg: str) -> t.NoReturn:
    """
    Report error and exit with specified non-zero exit code
    """
    rich_print(f":collision: [bold red]{msg}[/]", file=sys.stderr)
    raise typer.Abort()
