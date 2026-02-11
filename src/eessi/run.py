# license (SPDX): GPL-2.0-only
#
# authors:
# - Alex Domingo (Vrije Universiteit Brussel)

import subprocess

from rich import print as rich_print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from eessi.print import report_error


class CmdRunner:
    """
    Execute shell commands
    - as active user
    - as root with sudo
    """
    def __init__(self):
        self.sudo_password = None

    def ask_sudo_password(self, cmd: str) -> None:
        """
        Prompt the user to input the password for sudo
        """
        rich_print(
            ":rotating_light: The following command requires [bold red]root permissions[/]: "
            f"[dim cyan]{cmd}[/]"
        )
        return Prompt.ask(
            ":key: Enter your [bold yellow]user password[/] in this system:",
            password=True,
        )

    def run_cmd_user(self, cmd: str) -> tuple[str, str, int]:
        """
        Execute shell command as user

        Returns stdout, stderr, and exit code
        """
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return res.stdout, res.stderr, res.returncode

    def run_cmd_root(self, cmd: str) -> tuple[str, str, int]:
        """
        Execute shell command as root
        Supports sudo with password input

        Returns stdout, stderr, and exit code
        """
        if self.sudo_password is None:
            self.sudo_password = self.ask_sudo_password(cmd)

        proc = subprocess.Popen(
            ["sudo", "-S"] + cmd.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate(input=f"{self.sudo_password}\n")
        return stdout, stderr, proc.returncode

    def run_cmd_spinner(self, cmd: str, use_sudo: bool = False) -> tuple[str, str, int]:
        """
        Execute shell command
        Print command with a spinner in output

        - cmd: command to execute
        - use_sudo: whether to use sudo for this command

        Returns stdout, stderr, and exit code
        """
        cmd_runner = self.run_cmd_user
        description = f"Executing command: [dim cyan]{cmd}[/]"
        if use_sudo:
            cmd_runner = self.run_cmd_root
            description = f"Executing command as [bold red]root[/]: [dim cyan]{cmd}[/]"
            # password prompt must happen before spinner, otherwise it gets drawn over
            if self.sudo_password is None:
                self.sudo_password = self.ask_sudo_password(cmd)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=description, total=None)
            res = cmd_runner(cmd)
        cmd_status_mark = "white_check_mark" if res[2] == 0 else "collision"
        rich_print(f":{cmd_status_mark}: Command: [dim cyan]{cmd}[/]")

        return res

    def run_cmd_hidden(self, cmd: str, use_sudo: bool = False) -> tuple[str, str, int]:
        """
        Execute shell command
        Keep execution hidden, do not print feedback on output

        - cmd: command to execute
        - use_sudo: whether to use sudo for this command

        Returns stdout, stderr, and exit code
        """
        cmd_runner = self.run_cmd_user
        if use_sudo:
            cmd_runner = self.run_cmd_root
            if self.sudo_password is None:
                self.sudo_password = self.ask_sudo_password(cmd)

        return cmd_runner(cmd)

    def run_cmd(
        self,
        cmd: str,
        check: bool = True,
        show_cmd: bool = True,
        use_sudo: bool = False,
    ) -> tuple[str, str, int]:
        """
        Generic execution of shell command
        Switches to specific runners depending on given options

        - cmd: Command to execute
        - check: Whether to check for errors and report them
        - show_cmd: Whether to show the executing command with a spinner
        - use_sudo: Whether to use sudo for this command

        Returns stdout, stderr, and exit code
        """
        cmd_runner = self.run_cmd_hidden
        if show_cmd:
            cmd_runner = self.run_cmd_spinner

        res = cmd_runner(cmd, use_sudo=use_sudo)

        if check and res[2] != 0:
            report_error(f"Command failed: {cmd}; Output: {res[0]}; Error: {res[1]}")

        return res
