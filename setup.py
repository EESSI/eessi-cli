from setuptools import setup

setup(
    name="eessi-cli",
    version="0.0.1",
    description="EESSI command line interface",
    url="https://github.com/EESSI/eessi-cli",
    install_requires=["click>=8.0"],
    packages=["eessi/cli"],
    entry_points={
        "console_scripts": ["eessi=eessi.cli.main:main"],
    },
    python_requires=">=3.6",
)
