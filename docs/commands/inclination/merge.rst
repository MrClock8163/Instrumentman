Merging
=======

The results from each inclination measurement run are saved to separate CSV
files. If multiple measurements are from the same setup and need to be
processed together, the files need to be merged. The merging command provides
a convenience tool for this purpose.

Requirements
------------

- Inclination measurement files from previous measurements

.. note::

    The command does not do any semantic validation of the data in the
    specified files. It simply concatenates those rows from all files, that
    follow the required format.

Usage
-----

.. click:: instrumentman.inclination:cli_merge
    :prog: iman merge inclination
