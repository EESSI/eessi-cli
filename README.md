# EESSI command line interface

`eessi-cli` is a lightweight command line tool to help with using the European Environment for Scientific Software Installaitons (EESSI).

* Website: https://eessi.io
* Documentation: https://eessi.io/docs
* GitHub: https:/github.com/EESSI


## Installation

### From PyPI

```shell
pip install eessi-cli
```

### From source

```shell
pip install .
```


## Usage

### `init` subcommand

Use `eval` and `eessi init` to prepare your session environment for using EESSI.

```shell
eval "$(eessi init)"
```

To see which commands this would evaluate, just run `eessi init`.


## Design goals

* Easy to install and use.
* No dependencies beyond Python 3.6 (or newer) and its standard library.
