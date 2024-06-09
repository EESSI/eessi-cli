# license (SPDX): GPL-2.0-only
# 
# authors: Kenneth Hoste (Ghent University)

import os
import sys


def init(_):
    """
    Initialize shell environment for using EESSI
    """
    eessi_path = os.path.join("/cvmfs", "software.eessi.io", "versions", "2023.06")
    if os.path.exists(eessi_path):
        print("# Commands to prepare your session environment for using EESSI (https://eessi.io/docs)")
        print("# Use eval so commands below are used to set up your environment: eval \"$(eessi init)\"")
        print("source /cvmfs/software.eessi.io/versions/2023.06/init/bash")
    else:
        sys.stderr.write(f"ERROR: {eessi_path} does not exist!\n")
        eessi_docs_access = "https://eessi.io/docs/getting_access/is_eessi_accessible"
        sys.stderr.write(f"See {eessi_docs_access} for information on how to get access to EESSI.\n")
        sys.exit(1)
