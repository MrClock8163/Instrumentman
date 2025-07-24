# Changelog

## v0.2.0

First release of the applications in a new separate CLI package.
All CLIs are now based on Click and Click Extra, and registered as
subcommands under a common `iman` entry command.

### Added

- `iman` command line entry point
- GeoCom protocol tester (`test geocom`)
- GSI Online DNA protocol tester (`test gsidna`)
- file lister (`list files`)
- job lister (`list jobs`)
- file downloader (`download file`)
- inclination measurement (`measure inclination`)
- inclination calculation (`calc inclination`)
- inclination results merger (`merge inclination`)
- `morse` was extended with new options:
  - beep unit time option
  - more connection options
  - instrument compatibility option

### Changed

- all programs are now registered as subcommands under the `iman` command
- commands are now organized into command groups based on the type of action
  instead of context (e.g. all measurement type programs are now under the
  `measure` subcommand, instead of `setmeasurement measure`, `setup measure`,
  etc.)
- target definition creation is now not part of set measurement specifically
  (they will be used for other programs as well in the future)

### Fixed

- `terminal` app could not be launched with Python 3.11 due
  to an f-string error

## v0.1.0

Originally released as part of
[GeoComPy](https://github.com/MrClock8163/GeoComPy) v0.7.0

### Added

- Morse application
- Interactive Terminal application
- Set Measurement application
