Uploading
=========

Data can be uploaded to instruments through a serial connection, by simply
sending the file data line by line. Most instruments, that support data
uploads through serial, accept coordinate data in CSV format. Some instruments
also support their own specialized database record formats.

Requirements
------------

- Instrument capable of serial ASCII data transfer

.. caution::
    :class: warning

    Currently only ASCII encodable files can be uploaded. Older instruments
    do not accept special code pages like windows-1252 and other extended
    ASCII sets (especially not modern unicode), so accented characters have
    to be avoided.

Usage
-----

.. click:: instrumentman.datatransfer:cli_upload
    :prog: iman upload data
