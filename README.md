<h1 align="center">
<img src="https://raw.githubusercontent.com/mrclock8163/instrumentman/main/docs/iman_logo.png" alt="I-man logo" width="400">
</h1><br>

[![PyPI - Version](https://img.shields.io/pypi/v/instrumentman)](https://pypi.org/project/instrumentman/)
[![Python Version](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FMrClock8163%2FInstrumentman%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)](https://pypi.org/project/instrumentman/)
[![MIT](https://img.shields.io/github/license/mrclock8163/instrumentman)](https://opensource.org/license/mit)
[![Tests status](https://img.shields.io/github/actions/workflow/status/mrclock8163/instrumentman/run-tests.yml?label=linting)](https://github.com/MrClock8163/Instrumentman)
[![Docs status](https://app.readthedocs.org/projects/instrumentman/badge/?version=latest)](https://instrumentman.readthedocs.io/latest/)
[![Typed](https://img.shields.io/pypi/types/geocompy)](https://pypi.org/project/geocompy/)

Instrumentman (or I-man for short) is a Python CLI package, that is a
collection of automated measurement programs and related utilities for
surveying instruments (mainly Leica robotic total stations).

- **Download:** https://pypi.org/project/instrumentman/
- **Documentation:** https://instrumentman.readthedocs.io/
- **Source:** https://github.com/MrClock8163/Instrumentman
- **Bug reports:** https://github.com/MrClock8163/Instrumentman/issues

## Main features

- Pure Python implementation
- Support for type checkers
- Command line applications

## Requirements

To use the package, Python 3.11 or higher is required.

I-man relies on the
[GeoComPy](https://github.com/MrClock8163/GeoComPy) package for the
implementation of the various remote command protocols.

The individual commands require a number of other packages for command line
argument parsing, JSON manipulation, calculations and other functions.

## Installation

The preferred method to install I-man is through PyPI, where both wheel
and source distributions are made available.

```shell
python -m pip install instrumentman
```

If not yet published changes/fixes are needed, that are only available in
source, I-man can also be installed locally from source, without any
external tools. Once the repository is cloned to a directory, it can be
installed with pip.

```shell
git clone https://github.com/MrClock8163/Instrumentman.git
cd Instrumentman
python -m pip install .
```

## License

I-man is free and open source software, and it is distributed under the terms of the
[MIT License](https://opensource.org/license/mit).
