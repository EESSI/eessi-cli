# Changelog

## [0.1.1] - 2026-02-06

- avoid crash in `eessi check`: update `get_repo_attribute` to take into account that attribute value can be 0 byte value (empty) (#13)

## [0.1.0] - 2026-02-04

- use custom help option to control its placement and behaviour (PR #7)
- initial implementation of `eessi check` (PR #10)
- update CI workflow to test `eessi check` (PR #11)

## [0.0.5] - 2026-01-29

- require that EESSI version to use is specified in eessi shell via `--eessi-version` option (PR #3)
- force interactive shell for eessi shell + add tests for eessi shell in CI workflow (PR #4)
- Add option to display version and show help with no options (PR #5)

## [0.0.4] - 2026-01-29

- initial implementation for `eessi shell`
- repackage with modern PyPA standards (PR #2)

## [0.0.3] - 2026-01-29

- rename command to `eessi`

## [0.0.2] - 2026-01-29

- re-design using Typer, add placeholders for 'check' and 'shell' subcommands

## [0.0.1] - 2026-01-29

- initial release, with (very) basic `eessi-cli init` command (PR #1)
