Downloading
===========

Data downloading works by simply listening on the serial line, and saving
whatever the instrument sends. Some instruments have their own data formats
(maybe even a complete ASCII representation of their internal database), others
might use more common interchange formats.

Some formats have an end-of-file (EOF) marker, some instruments send an EOF
marker regardless of the format (e.g. when the transfer is finished a Trimble
M3 sends an EOF that is simply ``END``), this can be specified as an option to
automatically finish the transfer when this marker sequence is received.
Other formats (like the Leica GSI) do not have such a marker. In these cases
the transfer will be closed if no data was received in the timeout window
(timeout based automatic closing only occurs if the download at least started).
When the automatic closing is disabled, the transfer has to be manually closed
(with keyboard interrupt), once all data was received.

To help detecting when the transfer finished, the output is always printed
to the standard output, even if an output file is specified.

.. caution::
    :class: warning

    The output in the terminal might not be a 100% accurate representation of
    the received data. The data might by partially or completely binary, which
    cannot be accurately represented with ASCII characters in the terminal
    (non-ASCII bytes are replaced with ``?`` symbols in the terminal output).

Requirements
------------

- Instrument capable of serial ASCII data transfer

Examples
--------

.. code-block:: shell
    :caption: Downloading Trimble M5 format

    iman download data --eof END -b 38400 COM4 data.m5

Usage
-----

.. click:: instrumentman.datatransfer:cli_download
    :prog: iman download data
