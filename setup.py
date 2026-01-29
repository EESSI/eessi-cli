from setuptools import setup

setup(
    name="eessi",
    version="0.0.2",
    description="User-friendly command line interface to EESSI - https://eessi.io",
    url="https://github.com/EESSI/eessi-cli",
    install_requires=["typer>=0.21"],
    packages=["eessi/cli"],
    entry_points={
        "console_scripts": ["eessi-cli=eessi.cli.main:app"],
    },
    python_requires=">=3.9",
)
