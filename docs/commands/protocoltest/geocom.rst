GeoCom
======

The GeoCom protocol test suite runs commands from all GeoCom subsystems, to
see what part of the protocol might be usable on the instrument.

.. note::

    The command only does surface level testing by executing one command
    from each subsystem. The results are only informative, they might not be
    completely accurate. It might happen, that an instrument responds to the
    command used for testing, but does not actually respond to the other
    commands of the subsystem with valid data.

Requirements
------------

- GeoCom capable instrument

Usage
-----

.. click:: instrumentman.protocoltest:cli_geocom
    :prog: iman test geocom
