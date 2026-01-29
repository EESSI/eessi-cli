# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import subprocess
import sys
import tempfile
import typer
from rich import print as rich_print
from typing import Annotated

app = typer.Typer()


def report_error(msg, exit_code: int = 1):
    """
    Report error and exit with specified non-zero exit code
    """
    rich_print(f"[bold red]{msg}", file=sys.stderr)
    if exit_code <= 0:
        raise ValueError(f"Exit code should be positive non-zero integer, got {exit_code}")
    sys.exit(exit_code)


@app.command()
def shell(
    eessi_version: Annotated[str, typer.Option(help="EESSI version")] = '',
):
    """
    Create subshell in which EESSI is available and initialised
    """
    if not eessi_version:
        report_error("EESSI version to use is not specified, which is required!")

    init_file = tempfile.mkstemp()[1]
    with open(init_file, 'w') as fp:
        fp.write(f"set -e; source /cvmfs/software.eessi.io/versions/{eessi_version}/init/bash")

    res = subprocess.run(['/bin/bash', '--init-file', init_file, '-i'])
    if res.returncode != 0:
        report_error("ERROR: Non-zero exit code detected for interactive shell!", exit_code=res.returncode)
