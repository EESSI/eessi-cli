# EESSI command line interface

`eessi` is a lightweight command line tool to help with using the European Environment for Scientific Software Installaitons (EESSI).

* Website: https://eessi.io
* Documentation: https://eessi.io/docs
* GitHub: https:/github.com/EESSI


## Installation

### From PyPI

```shell
pip install eessi
```

### From source

```shell
pip install .
```


## Usage

Use `eessi --help` to get basic usage information.

### `check` subcommand

Check CernVM-FS setup for accessing EESSI

*(to be implemented)*


### `init` subcommand

Initialize shell environment for using EESSI

Use `eval` and `eessi init` to prepare your session environment for using EESSI.

```shell
eval "$(eessi init)"
```

To see which commands this would evaluate, just run `eessi init`.


### `shell` subcommand
    
Create subshell in which EESSI is available and initialised

*(to be implemented)*

## Design goals

* Easy to install and use.
* User-friendly and intuitive interface to using EESSI.
