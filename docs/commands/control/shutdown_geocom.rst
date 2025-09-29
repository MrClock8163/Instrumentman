Shutdown - GeoCOM
=================

For power management reasons, it might be required to deactivate some aspects
of an instrument to conserve power. 

Requirements
------------

- GeoCOM capable instrument

Examples
--------

.. code-block:: shell
    :caption: Shutting down the instrument

    iman shutdown geocom instrument COM1

.. code-block:: shell
    :caption: Deactivating GeoCOM online mode (only applicable before TPS1200)

    iman shutdown geocom protocol COM1

Usage
-----

.. click:: instrumentman.control:cli_shutdown_geocom
    :prog: iman shutdown geocom
