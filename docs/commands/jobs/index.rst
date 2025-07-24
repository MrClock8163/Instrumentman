:icon: material/archive-outline

Job Listing
===========

As an information-only feature, on newer instruments it is possible to
request the list of job files on the instrument. The job listing command
will display these files in a list (a job will typically have multiple
associated files, possibly the chunks, point code files, etc.).

Requirements
------------

- GeoCom capable instrument

Usage
-----

.. click:: instrumentman.jobs:cli_list
    :prog: iman list jobs
