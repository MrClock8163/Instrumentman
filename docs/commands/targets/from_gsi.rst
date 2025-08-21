Convert from GSI
================

A common output of Leica total stations is the Leica GSI format. Cartesian
coordinate and polar measurements can be converted to a target definition.

Requirements
------------

- Target point measurements in GSI8 or GSI16 format

Examples
--------

.. code-block:: shell
    :caption: Importing coordinates

    iman convert gsi-targets measurements.gsi targets.json

.. code-block:: shell
    :caption: Importing targets from polar measurements

    iman convert gsi-targets --station 1.212 -5.439 0.934 --iheight 0.000 measurements.gsi targets.json

.. code-block:: shell
    :caption: Importing targets with identical reflectors and target heights

    iman convert gsi-targets --reflector MINI --height 0.0 measurements.gsi targets.json

Usage
-----

.. click:: instrumentman.setup:cli_convert_gsi_to_targets
    :prog: iman convert gsi-targets
