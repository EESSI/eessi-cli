# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)
# authors: Davide Grassano (CECAM-EPFL)

from typing import Annotated

import typer

from eessi.cli.help import help_callback, version_callback

HELP = Annotated[bool, typer.Option(
    "-h",
    "--help",
    help="Show this message and exit aaaa.",
    callback=help_callback,
    is_eager=True,
)]

VERSION = Annotated[bool, typer.Option(
    "-v",
    "--version",
    help="Show version of eessi CLI.",
    callback=version_callback,
    is_eager=True,
)]
