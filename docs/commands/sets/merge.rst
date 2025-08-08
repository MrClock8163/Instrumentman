Merging
=======

The results of every set measurement session are saved to a separate file.
When multiple sessions are measured using the same targets from the same
station, the data files need to be merged to process them together.

.. note::

    The merge will be refused if the station information, or the target
    points do not match between the targeted sessions.

Requirements
------------

- Session result files from previous set measurements

Examples
--------

.. code-block:: shell
    :caption: Merging session results in directory

    iman merge sets merged.json sessions/setmeasurement_*.json

.. code-block:: shell
    :caption: Merging session results in multiple directories

    iman merge sets merged.json sessions1/measurements_*.json sessions2/measurements_*.json

Usage
-----

.. click:: instrumentman.setmeasurement:cli_merge
    :prog: iman merge sets
