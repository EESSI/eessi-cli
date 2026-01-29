# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import subprocess
import sys
import tempfile
import typer
from rich import print as rich_print

app = typer.Typer()


@app.command()
def shell():
    """
    Create subshell in which EESSI is available and initialised
    """
    init_file = tempfile.mkstemp()[1]
    with open(init_file, 'w') as fp:
        fp.write("set -e; source /cvmfs/software.eessi.io/versions/2023.06/init/bash")

    res = subprocess.run(['/bin/bash', '--init-file', init_file])
    if res.returncode != 0:
        rich_print("[bold red]ERROR: Non-zero exit code detected for interactive shell!", file=sys.stderr)
        sys.exit(res.returncode)
