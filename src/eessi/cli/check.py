# license (SPDX): GPL-2.0-only
#
# authors: Kenneth Hoste (Ghent University)

import os
import re
import subprocess

import typer
from rich import print as rich_print

from eessi.cli.help import help_callback

app = typer.Typer()


INFO = 'INFO'
OK = 'OK'
WARNING = 'WARNING'
ERROR = 'ERROR'

UNKNOWN = '[bold yellow] UNKNOWN'

CVMFS_ROOT = '/cvmfs'

CVMFS_CLIENT_SETTINGS = {
    # TODO: warn if path of client cache dir is in /tmp
    'CVMFS_CACHE_DIR': "Path to client cache directory",
    'CVMFS_CLIENT_PROFILE': "Client profile",
    # TODO: warn if there's only one
    'CVMFS_HTTP_PROXY': "Proxy servers",
    # TODO: warn if too small? (<1GB)
    'CVMFS_QUOTA_LIMIT': "Client cache quota limit",
    # TODO: warn if there's only one (and no proxies)
    'CVMFS_SERVER_URL': "List of Stratum-1 mirror servers",
    'CVMFS_SHARED_CACHE': "Shared cache",
    'CVMFS_USE_GEOAPI': "GeoAPI enabled",
}

# development repo with various sub-projects
# see also https://www.eessi.io/docs/repositories/dev.eessi.io
EESSI_DEV_REPO = 'dev.eessi.io'

# experimental repo for RISC-V,
# see also https://www.eessi.io/docs/repositories/riscv.eessi.io
EESSI_RISCV_REPO = 'riscv.eessi.io'

# main production repo,
# see also https://www.eessi.io/docs/repositories/software.eessi.io
EESSI_SOFTWARE_REPO = 'software.eessi.io'

EESSI_REPOS = [
    EESSI_DEV_REPO,
    EESSI_RISCV_REPO,
    EESSI_SOFTWARE_REPO,
]


def print_result(status: str, msg: str, indent_level: int = 0):
    """
    Print result for a specific check
    """
    indent = indent_level * 4 * ' '

    if status == OK:
        rich_print(f"{indent}:white_check_mark: {status} {msg}")
    elif status == INFO:
        rich_print(f"{indent}:information: {msg}")
    elif status == WARNING:
        rich_print(f"{indent}:zap: [yellow]{status} {msg}")
    elif status == ERROR:
        rich_print(f"{indent}:x: [bold red]{status} {msg}")
    else:
        rich_print(f"{indent}:{status}: {msg}")

def run_cmd(cmd: str):
    """
    Run shell command.

    Returns stdout, stderr, and exit code.
    """
    res = subprocess.run(cmd, shell=True, capture_output=True, universal_newlines=True)

    return (res.stdout, res.stderr, res.returncode)


def is_repo_available(repo: str):
    """
    Check if repo is available
    """
    repo_path = os.path.join(CVMFS_ROOT, repo)
    if os.path.isdir(repo_path):
        res = (OK, f"{repo_path} is available")
    else:
        res = (ERROR, f"{repo_path} is NOT available")

    return res


def get_repo_attribute(repo: str, key: str):
    """
    Get repository attribute
    """
    repo_path = os.path.join(CVMFS_ROOT, repo)

    value = UNKNOWN

    (stdout, stderr, exit_code) = run_cmd(f"attr -g {key} {repo_path}")
    if exit_code == 0:
        # Expected output is something like:
        #   Attribute "revision" had a 5 byte value for /cvmfs/software.eessi.io:
        #   13972
        #
        # If there's no value found ('0 byte value'), then last line is *empty*
        regex = re.compile("had a [1-9][0-9]* byte value", re.M)
        if regex.search(stdout):
            value = stdout.splitlines()[-1].strip()

    return value


def get_cvmfs_config_settings(repo: str, keys: list[str]):
    """
    Get values for specific CernVM-FS configuration settings
    """
    cmd = f"cvmfs_config showconfig {repo}"
    (stdout, stderr, exit_code) = run_cmd(cmd)

    values = {}
    for key in keys:
        regex = re.compile(f'^{key}=(?P<value>.*)', re.M)
        res = regex.search(stdout)
        if res:
            # value may be a list of items, like:
            # CVMFS_SERVER_URL='http://server.one;http://server.two' . # from /etc/cvmfs/default.local

            # cut off comment at the end
            value = res.group('value').split('#', 1)[0].rstrip()
            # strip single quotes at start/end
            value = value.strip("'")
            # split by semicolon for list values
            if ';' in value:
                value = value.split(';')

            values[key] = value
        else:
            values[key] = UNKNOWN

    return values


def reformat_for_humans(key: str, value: str):
    """
    Reformat value for specific CernVM-FS configuration setting for humans
    """
    if key == 'CVMFS_QUOTA_LIMIT' and value != UNKNOWN:
        gb = int(value) / 1024.
        value = f"{gb} GiB"

    return value


def check_cache_cleanups(repo: str, indent_level: int):
    """
    Check number of cache cleanups in last 24h
    """
    ncleanup24 = get_repo_attribute(repo, 'ncleanup24')
    msg = f"Number of cache cleanups in last 24h: {ncleanup24}"
    if ncleanup24 == UNKNOWN:
        status = ERROR
    else:
        ncleanup24 = int(ncleanup24)

        if ncleanup24 > 24:
            status = WARNING
            msg += " (cache quota limit too low?)"
        else:
            status = OK
    print_result(status, msg, indent_level=indent_level)


def check_repo(repo: str):
    """
    Checks for specified CernVM-FS repository
    """
    repo_path = os.path.join(CVMFS_ROOT, repo)

    print_result(*is_repo_available(repo), indent_level=1)

    revision = get_repo_attribute(repo, 'revision')
    status = ERROR if revision == UNKNOWN else INFO
    print_result(status, f"Revision (client): {revision}", indent_level=1)

    grouped_keys = {
        "Client cache": {
            'sigil': 'computer',
            'keys': ['CVMFS_CACHE_DIR', 'CVMFS_SHARED_CACHE', 'CVMFS_QUOTA_LIMIT'],
            'stat_fields': ["Cache Usage"],
            'other': [check_cache_cleanups],
        },
        "Server/proxy settings": {
            'sigil': 'globe_showing_europe-africa',
            'keys': ['CVMFS_SERVER_URL', 'CVMFS_HTTP_PROXY', 'CVMFS_USE_GEOAPI'],
        },
        "Other": {
            'sigil': 'information_desk_person',
            'keys': ['CVMFS_CLIENT_PROFILE'],
        },
    }

    cmd = f"cvmfs_config stat -v {repo}"
    stat_output, stderr, exit_code = run_cmd(cmd)
    if exit_code:
        # 'cvmfs_config stat' failed, just ignore here
        stat_output = ''

    for descr, specs in grouped_keys.items():
        print_result(specs['sigil'], f"{descr}:", indent_level=1)

        setting_values = get_cvmfs_config_settings(repo, specs['keys'])

        for key in specs['keys']:
            setting = CVMFS_CLIENT_SETTINGS[key]
            value = setting_values.get(key)
            value = reformat_for_humans(key, value)

            status = INFO
            if key == 'CVMFS_HTTP_PROXY' and value == 'DIRECT':
                status = WARNING
                value += " (not recommended, see https://eessi.io/docs/no-proxy)"

            if value is None:
                print_result(ERROR, f"{setting}: {UNKNOWN}", indent_level=2)
            else:
                if isinstance(value, list):
                    # indent list items by two levels
                    value = '\n' + '\n'.join(' ' * 4 * 3 + x for x in value)

                print_result(status, f"{setting}: {value}", indent_level=2)

        for field in specs.get('stat_fields', []):
            regex = re.compile(f"^{field}:(?P<value>.*)", re.M)
            res = regex.search(stat_output)
            if res:
                print_result(INFO, f"{field}: {res.group('value')}", indent_level=2)
            else:
                print_result(ERROR, f"Required field '{field}' not found!", indent_level=2)

        for other_check in specs.get('other', []):
            if callable(other_check):
                other_check(repo, indent_level=2)
            else:
                raise ValueError(f"{other_check} is not callable?!")


# TODO:
# download manifest from mirror:
# http://aws-eu-central-s1.eessi.science/cvmfs/software.eessi.io/.cvmfspublished
# with open('manifest', mode='rb') as fp:
#   manifest = fp.read()
# >>> [x for x in manifest.splitlines() if x.startswith(b'S')]
# [b'S13972']
# timestamp of revsion from server manifest: T1769765986


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
    rich_print(":package: Checking for EESSI repositories...")
    for repo in EESSI_REPOS:
        print_result(*is_repo_available(repo), indent_level=1)
    print('')

    repo = EESSI_SOFTWARE_REPO
    rich_print(f":magnifying_glass_tilted_right: Inspecting EESSI repository {repo}...")
    check_repo(repo=repo)
