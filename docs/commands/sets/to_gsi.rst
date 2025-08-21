Convert to GSI
==============

To help in further processing of the set measurements, the data can be
converted into the Leica GSI8 or GSI16 exchange formats.

Requirements
------------

- Session result files from previous set measurements

Examples
--------

.. code-block:: shell
    :caption: Converting with default units

    iman convert set-gsi set_measurement.json measurements.gsi

.. code-block:: shell
    :caption: Converting to specific units

    iman convert set-gsi --length-unit cmm --angle-unit gon set_measurement.json measurements.gsi

Usage
-----

.. click:: instrumentman.setmeasurement:cli_convert_set_to_gsi
    :prog: iman convert set-gsi


