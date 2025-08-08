Listing
=======

The most basic file management function is the ability to list files of
a specified type in a specified directory on a memory device of the instrument.

The listing command can be used to retrieve the list of files belonging to a
certain file type, or located in a certain directory. In addition to the
file name, the file size in bytes and the date of last modification is also
displayed.

Requirements
------------

- GeoCom capable instrument

Paths
-----

The most general way of file listing is to not specify a file type (defaulting
to unknown), and giving the directory path. Such a path should use ``/`` as
separators (contrary to other Windows conventions) and might end with a ``/``.

If a special type of file is to be listed (e.g. database), then it is enough
to specify the file type, the path can be left out.

.. note::

    On older instruments, the file listing might not return directories. In
    these cases the recursive file tree cannot be created.

Examples
--------

.. code-block:: shell
    :caption: Listing database files in internal memory

    iman list files -f database COM1

.. code-block:: shell
    :caption: Listing all exported files on a CF card

    iman list files -d cf COM1 Data

.. code-block:: shell
    :caption: Listing all contents of a directory recursively

    iman list files --depth 0 COM1 Data

Usage
-----

.. click:: instrumentman.filetransfer:cli_list
    :prog: iman list files
