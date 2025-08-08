Measurement
===========

Robotic total stations integrate dual axis compensators, that can measure
the crosswise and lengthwise inclination of the instrument. The accuracy of
these measurements is usually in the domain of arcseconds. If the inclination
has to be known with better reliability, multiple measurements have to be
taken, preferably in different horizontal positions of the instrument.

Requirements
------------

- GeoCom capable robotic total station

Results
-------

The measurements can be saved to a file in CSV format. The output contains
the horizontal angle that the instrument was facing at the moment of the
measurement, the cross inclination and the length inclination. If the
instrument was oriented to an existing coordinate system at the time, then the
horizontal angles are whole circle bearings in that system, otherwise they
are relative to the arbitrary orientation.

Examples
--------

.. code-block:: shell
    :caption: Measure in 3 positions, starting from hz=0 and print results

    iman measure inclination -z -p 3 COM1

.. code-block:: shell
    :caption: Measure 2 cycles of 3 positions and save results in CSV

    iman measure inclination -c 2 -p 3 -o inclination.csv COM1
    

Usage
-----

.. click:: instrumentman.inclination:cli_measure
    :prog: iman measure inclination
