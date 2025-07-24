Importing
=========

If the coordinates of the targets are known from a separate survey, the
targets definition can be created by importing the data from CSV format.

Requirements
------------

- point coordinates in CSV format

Prism type
----------

To create a targets definition, the prism types must be known at the target
points. It must be given as an argument to the command. If not every target
has the same prism type set up on it, the most common type should be given,
then the rest can be manually "fixed" in the saved JSON file.

Examples
--------

.. code-block:: shell
    :caption: Importing data and skipping code column in CSV

    iman import targets -c P_ENZ MINI coordinates.csv targets.json

Usage
-----

.. click:: instrumentman.setup:cli_import
    :prog: iman import targets
