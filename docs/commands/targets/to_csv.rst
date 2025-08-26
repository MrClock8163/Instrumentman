Convert to CSV
==============

If necessary, the target definition can be converted into an ordinary CSV
coordinate list file for easier use in other applications.

Requirements
------------

- Target definition JSON file

Examples
--------

.. code-block:: shell
    :caption: Exporting coordinates

    iman convert targets-csv -c pt -c e -c n -c h targets.json targets.csv

Usage
-----

.. click:: instrumentman.setup:cli_convert_targets_to_csv
    :prog: iman convert targets-csv
