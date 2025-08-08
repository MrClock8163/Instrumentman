Calculation
===========

After the measurements are done, the average inclination and the deviation
can be calculated from the results. The results give the coordinate system
axis-aligned inclination components and standard deviations, as well as the
resulting inclination and its direction.

Requirements
------------

- Inclination measurement files from previous measurements

Methodology
-----------

In each horizontal position 2 angles are given. The calculation is carried
out with the following general steps:

#. For each position

   #. Calculate cross and length offset of the standing axis 1 meter above
      the measurement center.
   #. Convert cross-length coordinates to polar
   #. Correct inclination direction with instrument bearing
   #. Convert polar inclination back to coordinates

#. Calculate mean and deviation of inclination coordinates
#. Convert mean coordinates to angles for axis-aligned results
#. Convert mean coordinates to polar inclination

Results can be either printed to the terminal, or saved a CSV file.

Usage
-----

.. click:: instrumentman.inclination:cli_calc
    :prog: iman calc inclination
