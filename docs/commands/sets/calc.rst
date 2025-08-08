Calculation
===========

The most common calculation needed after set measurements is the determination
of the target coordinates, from results of multiple measurement sessions and/or
cycles. The resulting coordinates (as well as their deviations) are saved
to a simple CSV file.

Requirements
------------

- Session result file from previous set measurement

Examples
--------

.. code-block:: shell
    :caption: Saving results with millimeter precision

    iman calc sets -p 3 merged.json results.csv

.. code-block:: shell
    :caption: Saving results with header and custom delimiter

    iman calc sets --header -d ; merged.json results.csv

Usage
-----

.. click:: instrumentman.setmeasurement:cli_calc
    :prog: iman calc sets
