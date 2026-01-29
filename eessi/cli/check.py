# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import typer

app = typer.Typer()


@app.command()
def check():
    """
    Check CernVM-FS setup for accessing EESSI
    """
    raise NotImplementedError
