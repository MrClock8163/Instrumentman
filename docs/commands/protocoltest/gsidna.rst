GSI Online DNA
==============

The GSI Online DNA protocol test suite executes one of each main commands
types of the system to see, which types the instrument accepts. A ``CONF``
and a ``SET`` command are executed first to check if read-writes to the
instrument settings are available. Then a ``GET`` and a ``PUT`` command is
run to test if the GSI based measurement/database commands are responsive.

Requirements
------------

- GSI Online DNA capable instrument

Usage
-----

.. click:: instrumentman.protocoltest:cli_gsidna
    :prog: iman test gsidna
