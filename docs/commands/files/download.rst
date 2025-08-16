Downloading
===========

A useful file management feature that gives the ability to download a file from
the instrument. The download command can be used to download a file identified
by either a file name and type, or a full file path.

.. caution::
    :class: warning

    File downloads over serial (especially Bluetooth) are rather slow, and
    greatly affected by the communication speed settings.

Requirements
------------

- GeoCom capable instrument

Process
-------

The download process is carried out by exchanging chunks of data. The
individual chunks are sent down by the instrument, and slowly reassambled on
the receiving side. The block size can be customized, but the maximum is 450
hex characters/block (or 225 bytes). Newer instruments support large file
downloads, where the block size can be increased up to 1800 characters/block.

Under normal circumstances it is recommended to use the maximum chunk size,
as this results in the fastest transfer. If the connection is not completely
reliable, decreasing the chunk size might reduce the size of data, that needs
to be resent due to timed out exchanges.

Examples
--------

.. code-block:: shell
    :caption: Downloading the root file of a job

    iman download file -f database COM1 job.xcf job.xcf

    // or
    
    iman download file COM1 DBX/job.xcf job.xcf

.. code-block:: shell
    :caption: Downloading an exported file from a CF card

    iman list files -d cf COM1 Data/coordinates.txt coordinates.txt

Usage
-----

.. click:: instrumentman.filetransfer:cli_download
    :prog: iman download file
