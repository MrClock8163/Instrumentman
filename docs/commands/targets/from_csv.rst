Convert from CSV
================

A target point definition can be created by importing the point coordinates
from a variable column CSV file. Coordinate and point name columns are
mandatory.

Requirements
------------

- Target point coordinates in CSV format

Examples
--------

.. code-block:: shell
    :caption: Importing coordinates

    iman convert csv-targets -c pt -c e -c n -c h targets.csv targets.json

.. code-block:: shell
    :caption: Importing targets with matching prisms and target heights

    iman convert csv-targets -c pt -c e -c n -c h --reflector MINI --height 0.12 targets.csv targets.json

.. code-block:: shell
    :caption: Importing coordinates but ignoring second (possibly code) column in CSV

    iman convert csv-targets -c pt -c ignore -c e -c n -c h targets.csv targets.json

Usage
-----

.. click:: instrumentman.setup:cli_convert_csv_to_targets
    :prog: iman convert csv-targets
