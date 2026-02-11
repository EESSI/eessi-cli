# license (SPDX): GPL-2.0-only
#
# authors:
# - Alex Domingo (Vrije Universiteit Brussel)

import os
import re
import tempfile
import typing as t
import urllib.error as urlerr
import urllib.request as urlreq
from enum import Enum

import typer
from rich import print as rich_print
from rich.padding import Padding
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.tree import Tree

from eessi.cli.help import help_callback
from eessi.print import report_error
from eessi.run import CmdRunner

app = typer.Typer()
runner = CmdRunner()

# Default values for CernVM-FS configuration
class CVMFSClientProfiles(str, Enum):
    single = "single"
    cluster = "cluster"

DEFAULT_CVMFS_CLIENT_FILE = "/etc/cvmfs/default.local"
DEFAULT_CVMFS_CLIENT_PROFILE = CVMFSClientProfiles.single
DEFAULT_CVMFS_QUOTA_LIMIT = 10000
DEFAULT_CVMFS_CACHE_DIR = "/var/lib/cvmfs"

URL_CVMFS_RELEASE_RPM = "https://cvmrepo.s3.cern.ch/cvmrepo/yum/cvmfs-release-latest.noarch.rpm"
URL_CVMFS_RELEASE_DEB = "https://cvmrepo.s3.cern.ch/cvmrepo/apt/cvmfs-release-latest_all.deb"
URL_CVMFS_EESSI_RPM = "https://github.com/EESSI/filesystem-layer/releases/download/latest/cvmfs-config-eessi-latest.noarch.rpm"
URL_CVMFS_EESSI_DEB = "https://github.com/EESSI/filesystem-layer/releases/download/latest/cvmfs-config-eessi_latest_all.deb"


def download_remote_file(url: str, filename: t.Optional[str] = None) -> str:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Downloading: {url}", total=None)
        try:
            local_path, _ = urlreq.urlretrieve(url, filename=filename)
        except urlerr.HTTPError as e:
            report_error(f"Download failed with HTTP error: {e.code}")
        except urlerr.URLError as e:
            report_error(f"Failed to reach a server: {e.reason}")
        except urlerr.ContentTooShortError as e:
            report_error(f"Download interrupted: {e.content}")
        else:
            rich_print(f":white_check_mark: Downloaded {url}")
    return local_path


def download_and_install_remote_deb(url: str) -> None:
    """
    Download DEB file from given URL and install it with dpkg
    Use temporary directory
    """
    filename = os.path.basename(url)
    if os.path.splitext(filename)[1] != ".deb":
        report_error(f"Cannot install file '{filename}' in Debian-based system")

    original_workdir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp_workdir:
        os.chdir(tmp_workdir)
        local_pkg = download_remote_file(url, filename=filename)
        runner.run_cmd(
            f"dpkg -i {local_pkg}",
            use_sudo=True,
        )
    os.chdir(original_workdir)


def get_package_manager() -> t.Optional[str]:
    """
    Determine which package manager is available on the system
    """
    supported_package_managers = ["yum", "dnf", "apt"]

    for pkgmgr in supported_package_managers:
        try:
            _, _, exit_code = runner.run_cmd(
                f"command -v {pkgmgr}",
                check=False,
                show_cmd=False,
            )
            if exit_code == 0:
                return pkgmgr
        except Exception:
            pass

    return None


def is_cvmfs_installed() -> bool:
    """Check if CernVM-FS is installed"""
    _, _, exit_code = runner.run_cmd(
        "cvmfs_config showconfig",
        check=False,
        show_cmd=False,
    )
    return exit_code == 0


def is_eessi_config_installed() -> bool:
    """Check if EESSI configuration is installed"""
    return os.path.exists("/etc/cvmfs/domain.d/eessi.io.conf")


def is_client_config_installed(config_file: str = DEFAULT_CVMFS_CLIENT_FILE) -> bool:
    """
    Check if client configuration file exists and contains required settings
    """
    client_profile = None
    quota_limit = None

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as fp:
                content = fp.read()
                client_profile = re.search("CVMFS_CLIENT_PROFILE", content)
                quota_limit = re.search("CVMFS_QUOTA_LIMIT", content)
        except PermissionError:
            report_error(f"Failed to read existing client configuration file for CernVM-FS: {config_file}")

    return client_profile and quota_limit


def install_cvmfs() -> None:
    """Install CernVM-FS based on the Linux distribution"""

    if is_cvmfs_installed():
        rich_print(":white_check_mark: CernVM-FS is already installed")
        return

    install_confirmation = Confirm.ask("CernVM-FS not found. Do you want to install CernVM-FS in this system?")
    if not install_confirmation:
        raise typer.Abort()

    rich_print(Padding(":package: Installing CernVM-FS packages...", (1, 0, 0, 0)))

    package_manager = get_package_manager()

    if package_manager in ["yum", "dnf"]:
        rich_print(":white_check_mark: Detected RHEL-based distribution")
        runner.run_cmd(
            f"{package_manager} install -y {URL_CVMFS_RELEASE_RPM}",
            use_sudo=True,
        )
        runner.run_cmd(
            f"{package_manager} install -y cvmfs",
            use_sudo=True,
        )

    elif package_manager == "apt":
        rich_print(":white_check_mark: Detected Debian-based distribution")
        download_and_install_remote_deb(URL_CVMFS_RELEASE_DEB)
        runner.run_cmd(
            "apt update",
            use_sudo=True,
        )
        runner.run_cmd(
            "apt install -y cvmfs",
            use_sudo=True,
        )
    else:
        report_error(
            "No supported package manager found. Only yum/dnf (RHEL-based) and apt (Debian-based) "
            "distributions are supported."
        )

    if is_cvmfs_installed():
        rich_print(":tada: CernVM-FS installed successfully")
    else:
        report_error("verification of CernVM-FS installation failed")


def install_eessi_config() -> None:
    """Install EESSI configuration for CernVM-FS"""

    if is_eessi_config_installed():
        rich_print(":white_check_mark: EESSI configuration is already installed")
        return

    install_confirmation = Confirm.ask("EESSI configuration not found. Do you want to install it in this system?")
    if not install_confirmation:
        raise typer.Abort()

    rich_print(Padding(":package: Installing EESSI configuration for CernVM-FS...", (1, 0, 0, 0)))

    package_manager = get_package_manager()

    if package_manager in ["yum", "dnf"]:
        rich_print(":white_check_mark: Detected RHEL-based distribution")
        runner.run_cmd(
            f"{package_manager} install -y {URL_CVMFS_EESSI_RPM}",
            use_sudo=True,
        )
    elif package_manager == "apt":
        rich_print(":white_check_mark: Detected Debian-based distribution")
        download_and_install_remote_deb(URL_CVMFS_EESSI_DEB)
    else:
        report_error(
            "No supported package manager found. Only yum/dnf (RHEL-based) and apt (Debian-based) "
            "distributions are supported."
        )

    if is_eessi_config_installed():
        rich_print(":tada: EESSI configuration for CernVM-FS installed successfully")
    else:
        report_error("verification of EESSI configuration for CernVM-FS failed")


def create_client_config(
    cache_dir: str = DEFAULT_CVMFS_CACHE_DIR,
    config_file: str = DEFAULT_CVMFS_CLIENT_FILE,
    quota_limit: int = DEFAULT_CVMFS_QUOTA_LIMIT,
    client_profile: str = DEFAULT_CVMFS_CLIENT_PROFILE,
) -> None:
    """Create client configuration file for CernVM-FS"""

    if is_client_config_installed(config_file=config_file):
        rich_print(":white_check_mark: CernVM-FS client configuration is already installed")
        return

    install_confirmation = Confirm.ask(
        "CernVM-FS client configuration not found. Do you want to install it in this system?"
    )
    if not install_confirmation:
        raise typer.Abort()

    rich_print(":package: Creating client configuration file...")

    config_content = [
        f"CVMFS_CLIENT_PROFILE='{client_profile.value}'",
        f"CVMFS_QUOTA_LIMIT={quota_limit}",
    ]
    # Add cache directory if it's not the default
    if cache_dir != DEFAULT_CVMFS_CACHE_DIR:
        config_content.append(f"CVMFS_CACHE_BASE={cache_dir}")

    with tempfile.NamedTemporaryFile(mode="w", delete_on_close=False) as fp:
        fp.writelines(f"{line}\n" for line in config_content)
        fp.close()
        rich_print(":white_check_mark: Configuration parameters added to temporary file")
        runner.run_cmd(
            f"cp {fp.name} {config_file}",
            use_sudo=True,
        )
        runner.run_cmd(
            f"chmod 644 {config_file}",
            show_cmd=False,
            use_sudo=True,
        )

    if is_client_config_installed(config_file=config_file):
        rich_print(f":tada: Client configuration file created at {config_file}")
    else:
        report_error("verification of client configuration for CernVM-FS failed")


def setup_eessi() -> None:
    """Run cvmfs_config setup to make EESSI CernVM-FS repository accessible"""

    rich_print(":package: Running cvmfs_config setup to configure EESSI repositories...")
    runner.run_cmd(
        "cvmfs_config setup",
        use_sudo=True,
    )

    rich_print(":white_check_mark: EESSI repositories configured successfully")


def native_install(
    cache_dir: str = DEFAULT_CVMFS_CACHE_DIR,
    config_file: str = DEFAULT_CVMFS_CLIENT_FILE,
    quota_limit: int = DEFAULT_CVMFS_QUOTA_LIMIT,
    client_profile: str = DEFAULT_CVMFS_CLIENT_PROFILE,
) -> None:
    """
    Install EESSI natively on the local host by:
    1. Installing CernVM-FS if not already installed
    2. Installing EESSI configuration for CernVM-FS if not already installed
    3. Creating client configuration file for CernVM-FS if not already installed
    """
    rich_print(Padding(":rocket: Launching native EESSI installation...", (1, 0)))

    task_list = Tree("EESSI requires the following components:")
    task_list.add("[underline blue][link=https://cernvm.cern.ch/fs]CernVM File System[/link][/]")
    task_list.add("configuration files of EESSI for CernVM-FS")
    task_list.add("client configuration files for CernVM-FS")
    task_list.add("EESSI repositories")
    rich_print(task_list)

    # Check and install CernVM-FS if needed
    rich_print(Padding(":jigsaw: [green]Step 1 of 4: [bold]CernVM-FS[/]", (1, 0)))
    install_cvmfs()

    # Check and install EESSI configuration if needed
    rich_print(Padding(":jigsaw: [green]Step 2 of 4: [bold]EESSI configuration for CernVM-FS[/]", (1, 0)))
    install_eessi_config()

    # Check and create client configuration if needed
    rich_print(Padding(":jigsaw: [green]Step 3 of 4: [bold]client configuration for CernVM-FS[/]", (1, 0)))
    create_client_config(cache_dir, config_file, quota_limit, client_profile)

    # Setup EESSI repositories
    rich_print(Padding(":jigsaw: [green]Step 4 of 4: [bold]EESSI repositories[/]", (1, 0)))
    setup_eessi()

    rich_print(Padding(":checkered_flag: Native EESSI installation completed successfully!", (1, 0)))


@app.command()
def install(
    help: bool = typer.Option(
        None,  # default value
        "-h",
        "--help",
        help="Show this message and exit.",
        callback=help_callback,
        is_eager=True,
    ),
    cache_dir: str = typer.Option(
        DEFAULT_CVMFS_CACHE_DIR,
        help="Directory for CernVM-FS client cache",
    ),
    config_file: str = typer.Option(
        DEFAULT_CVMFS_CLIENT_FILE,
        help="Path to client configuration file for CernVM-FS",
    ),
    quota_limit: int = typer.Option(
        DEFAULT_CVMFS_QUOTA_LIMIT,
        help="CernVM-FS client cache quota limit in MB",
    ),
    client_profile: CVMFSClientProfiles = typer.Option(
        DEFAULT_CVMFS_CLIENT_PROFILE,
        help="CernVM-FS client operation profile",
    ),
):
    """
    Install EESSI natively on the local host

    This command will carry out the following tasks:
    1. Install CernVM-FS system-wide
    2. Install EESSI configuration for CernVM-FS
    3. Configure CernVM-FS client

    [i]Note: This command requires [red]root privileges[/].
    """
    native_install(
        cache_dir=cache_dir,
        config_file=config_file,
        quota_limit=quota_limit,
        client_profile=client_profile,
    )
    rich_print("You can now use EESSI by running 'eessi init' or 'eessi shell'")


if __name__ == "__main__":
    app()
