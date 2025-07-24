Overview
========

Instrumentman (or I-man for short) is a collection of automated measurement
and processing CLI programs for surveying instruments. It originally started
out as the `apps` sub-package of
`GeoComPy <https://github.com/MrClock8163/GeoComPy>`_, but ended up being
split off into it's own project. The different programs are organized into an
easy-to-navigate CLI command system.

Since GeoComPy is mainly built around the Leica GeoCOM ASCII protocol (with
some additions like GSI Online DNA support), most programs are targeting
instruments that support this command set (primarily robotic total stations).

In addition to the measurement programs themselves, I-man includes various
utility commands, and processing commands as well, that cover the most
typical post-processing tasks.

Features
--------

- Pure Python implementation
- Unified CLI command structure
- Measurement programs
- Utility commands
- Processing commands

Requirements
------------

- Python 3.11 or newer
- `GeoComPy <https://github.com/MrClock8163/GeoComPy>`_ package
- `Click <https://click.palletsprojects.com/en/stable/>`_ and
  `Click Extra <https://kdeldycke.github.io/click-extra/>`_ CLI kits
- various other command specific depencies

Installation
------------

After installation, the commands can be accesed through the `iman` entry
command.

.. code-block:: shell

    iman -h

If the above direct entry does not work, the package can also be launched
as a Python module.

.. code-block:: shell

    python -m instrumentman -h

.. tip::

    As with any Python package, it might be advisable to install I-man in
    an isolated enviroment, like a virtual enviroment for more complex
    projects.

From PyPI
^^^^^^^^^

I-man is hosted on PyPI, therefore it can be installed with ``pip``.
Package dependencies are automatically handled.

.. code-block:: shell
    :caption: Installing from PyPI

    pip install instrumentman

From source
^^^^^^^^^^^

Download the release archive from
`PyPI <https://pypi.org/project/instrumentman/>`_, or from 
`GitHub releases <https://github.com/MrClock8163/Instrumentman/releases>`_.
Unpack the archive to a suitable place, and enter the ``instrumentman-x.y.z``
directory. Build and install the package with the following command:

.. code-block:: shell
    :caption: Building and installing locally

    python -m pip install .

Connections
-----------

The most straight forward and reliable connection to surveying instruments is
through a direct serial cable. The communication speed (baud) set on the
instrument must be in sync with the value provided to the measurement
commands.

If cable connection is not possible, communication is still possible through
serial profile classic Bluetooth (if the instrument has the capability). This
is usually more involved to set up. The Blutooth interface has to be activated
on the instrument and enabled for command exchange. The instrument also has to
be paired to the controlling computer.

.. note::

    An in-depth description of the Bluetooth connection setup process can be
    found in the
    `GeoComPy documentation <https://geocompy.readthedocs.io/stable/connections/>`_.
