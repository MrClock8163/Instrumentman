Uploading
=========

If a station setup was calculated separately (not using the on-board software),
it has to be uploaded to the instrument. This command allows to set the station
coordinates, instrument height and orientation.

.. note::

    The station name cannot be set. It will remain the last point name set with
    the on-board software.

Requirements
------------

- GeoCom capable total station

Usage
-----

.. click:: instrumentman.station:cli_upload
    :prog: iman upload station
