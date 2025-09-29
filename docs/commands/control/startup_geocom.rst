Startup - GeoCOM
=================

If an instrument system was deactivated, it might be necessary to reactivate it
before using certain capabilities of the instrument.

Requirements
------------

- GeoCOM capable instrument

Examples
--------

.. code-block:: shell
    :caption: Activating laser pointer

    iman startup geocom pointer COM1

Usage
-----

.. click:: instrumentman.control:cli_startup_geocom
    :prog: iman startup geocom
