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

```shell
eessi check
```

Example output:
```
📦 Checking for EESSI repositories...
    ✅ OK /cvmfs/dev.eessi.io is available
    ✅ OK /cvmfs/riscv.eessi.io is available
    ✅ OK /cvmfs/software.eessi.io is available

🔎 Inspecting EESSI repository software.eessi.io...
    💻 Client cache:
        ℹ Path to client cache directory: /var/lib/cvmfs/shared
        ℹ Shared cache: yes
        ℹ Client cache quota limit: 9.765625 GiB
        ℹ Cache Usage:  282k / 10240001k
    🌍 Server/proxy settings:
        ℹ List of Stratum-1 mirror servers:
            http://aws-eu-central-s1.eessi.science/cvmfs/software.eessi.io
            http://azure-us-east-s1.eessi.science/cvmfs/software.eessi.io
            http://cvmfs-ext.gridpp.rl.ac.uk:8000/cvmfs/software.eessi.io
        ⚡ WARNING Proxy servers: DIRECT (not recommended, see https://eessi.io/docs/no-proxy)
        ℹ GeoAPI enabled: yes
    💁 Other:
        ℹ Client profile:
```

If CernVM-FS is not available at all:
```
eessi check
📦 Checking for EESSI repositories...
    ❌ ERROR /cvmfs/dev.eessi.io is NOT available
    ❌ ERROR /cvmfs/riscv.eessi.io is NOT available
    ❌ ERROR /cvmfs/software.eessi.io is NOT available

🔎 Inspecting EESSI repository software.eessi.io...
    💻 Client cache:
        ℹ Path to client cache directory:  UNKNOWN
        ℹ Shared cache:  UNKNOWN
        ℹ Client cache quota limit:  UNKNOWN
        ❌ ERROR Required field 'Cache Usage' not found!
    🌍 Server/proxy settings:
        ℹ List of Stratum-1 mirror servers:  UNKNOWN
        ℹ Proxy servers:  UNKNOWN
        ℹ GeoAPI enabled:  UNKNOWN
    💁 Other:
        ℹ Client profile:  UNKNOWN
```

### `init` subcommand

Initialize shell environment for using EESSI

Use `eval` and `eessi init` to prepare your session environment for using EESSI.

```shell
eval "$(eessi init)"
```

To see which commands this would evaluate, just run `eessi init`.


### `shell` subcommand
    
Create subshell in which EESSI is available and initialised

```shell
eessi shell --eessi-version 2025.06
```

You *must* specify the EESSI version to use, there is no default value for this.

## Design goals

* Easy to install and use.
* User-friendly and intuitive interface to using EESSI.
