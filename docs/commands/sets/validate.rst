Validation
==========

After the measurement sessions are finished, it might be useful to validate,
that each session succeeded, no points were skipped.

Requirements
------------

- Session result files from previous set measurements

Examples
--------

.. code-block:: shell
    :caption: Validating session results in directory

    iman validate sets sessions/setmeasurement_*.json

.. code-block:: shell
    :caption: Validating session results in multiple directories

    iman validate sets sessions1/measurements_*.json sessions2/measurements_*.json

Usage
-----

.. click:: instrumentman.setmeasurement:cli_validate
    :prog: iman validate sets
