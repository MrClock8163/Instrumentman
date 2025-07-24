Measurement
===========

If the coordinates of the target points are not yet known (from network
establishing survey for example), the targets definition can be created
from quick new measurements.

The program is interactive. It will give instructions in the terminal at
each step. For each point some data is requested, then the target must be
aimed at.

.. caution::
    :class: warning

    The appropriate prism type needs to be set on the instrument before
    recording each target point. The program will automatically request
    the type from the instrument after the point is measured.

    This is needed, because the automated measurement programs support target
    series with mixed reflector types. The prism types are set according to
    the targets definition during the measurements.

Requirements
------------

- GeoCom capable robotic total station with ATR

Usage
-----

.. click:: instrumentman.setup:cli_measure
    :prog: iman measure targets
