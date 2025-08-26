# Changelog

All notable changes in the Instrumentman project will be documented in this
file.

The project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.4.0 (2025-08-26)

### Added

- Added aliases to multiple commands and command groups
- Added resection calculation logic
- Added station calculation (`calc station`) using resection from set
  measurements
- Added station uploading (`upload station`) to set station coordinates and
  orientation
- Added CSV to targets JSON conversion (`convert csv-targets`)
- Added targets JSON to CSV conversion (`convert targets-csv`)
- Added GSI to targets JSON conversion (`convert gsi-targets`)
- Added targets JSON to GSI conversion (`convert targets-gsi`)
- Added set measurement JSON to GSI conversion (`convert set-gsi`)
- Added logging options to `iman` root command
- Added logging to instrument connected commands
- Added `dateformat` option to set measurement
- Added `timeformat` option to set measurement

### Changed

- `geocompy` dependency minimum version was bumped to `v0.12.0`
- Updated descriptions in command helps
- Updated file listing to display results in a tree view
- Reworked file listing to be able to run recursively to build full tree view
- Protocol tests now display results in a table
- Inclination measurement now displays results in table
- Job listing now displays results in table
- Added progress indicator to more commands
- `points` option in set measurement and station calculation is now a multi
  option, instead of a comma separated string list
- `chunk` option of file download now expects size in bytes, instead of
  encoded hex characters
- Second argument (`output`) of set measurement now expects a file path or file
  path template instead of a directory

### Fixed

- Job listing could only be done once as the finializer command was so far
  missing from GeoComPy (the listing was left unclosed, and could not be
  set up again, only after an instrument restart)
- Target measurement would indefinitely halt on confirmation prompt

### Removed

- Removed importer command group and subcommands (`import`)
- Removed logging options from set measurement
- Removed `format` option from set measurement

## v0.3.0 (2025-08-01)

### Added

- serial data downloader (`download data`)
- serial data uploader (`upload data`)
- instrument settings saver (`download settings`)
- instrument settings loader (`upload settings`)
- `terminal` was extended with new settings:
  - baud
  - timeout

### Changed

- all package dependencies now have their minimum compatible version specified

### Fixed

- the connection test function in the `terminal` app did not work properly
  with GSI Online DNA protocol

## v0.2.0 (2025-07-25)

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

## v0.1.0 (2025-06-29)

Originally released as part of
[GeoComPy](https://github.com/MrClock8163/GeoComPy) v0.7.0

### Added

- Morse application
- Interactive Terminal application
- Set Measurement application
