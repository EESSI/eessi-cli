# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import typer

app = typer.Typer()


@app.command()
def shell():
    """
    Create subshell in which EESSI is available and initialised
    """
    raise NotImplementedError
