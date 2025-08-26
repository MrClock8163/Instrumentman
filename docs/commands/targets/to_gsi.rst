Convert to GSI
==============

Sometimes it is necessary to use the target coordinates for further
measurements. To simplify the process, the targets definition file can be
converted into a Leica GSI8 or GSI16 file, which is a common exchange format
for Leica instruments.

Requirements
------------

- Target definition JSON file

Examples
--------

.. code-block:: shell
    :caption: Exporting coordinates

    iman convert targets-gsi targets.json targets.gsi

.. code-block:: shell
    :caption: Exporting coordinates to GSI16 with 0.00001m precision

    iman convert targets-gsi --gsi16 --precision cmm targets.json targets.gsi

Usage
-----

.. click:: instrumentman.setup:cli_convert_targets_to_gsi
    :prog: iman convert targets-gsi

