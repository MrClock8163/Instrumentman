Calculation
===========

Resection calculation is commonly used when setting up an instrument on an
unkown point. Alternatively resection can be used in monitoring setups as well,
to handle the possible movement of the instrument between measurement cycles,
and to verify the integrity of the control points. The resection
calculation will always have excess measurements, which means it can be
adjusted with least squares, that provides standard deviations. If the
deviations of the resection suddenly increase in one of the cycles, it likely
indicates, that one of the control points moved.

The resection is done in two steps, separate horizontal and vertical
calculations.

Requirements
------------

- Session result file from previous set measurement

Usage
-----

.. click:: instrumentman.station:cli_calc
    :prog: iman calc station
