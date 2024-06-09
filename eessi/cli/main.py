# license (SPDX): GPL-2.0-only
# 
# authors: Kenneth Hoste (Ghent University)

import argparse
import sys

from eessi.cli.init import init


def main():
    parser = argparse.ArgumentParser(prog="eessi", description="EESSI command line utility")
    subparsers = parser.add_subparsers(help="Available subcommands")

    init_descr = "Initialize shell environment for using EESSI"
    parser_init = subparsers.add_parser("init", description=init_descr, help=init_descr)
    parser_init.set_defaults(func=init)

    args = parser.parse_args(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
