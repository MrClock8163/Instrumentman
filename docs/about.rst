Information
===========

Command Structure
-----------------

Different applications might implement multiple different commands, that are
relevant to the task. While these are defined and documented in application
subpackages, on the user level, the commands are grouped into action based
command groups instead for easier use.

For instance, the Set Measurement application defines commands for conducting
the measurements themselves, validating and merging multiple session outputs,
and also for calculating results. These can be accessed through the following
commands:

.. code-block:: shell

    iman measure sets -h
    iman merge sets -h
    iman validate sets -h
    iman calc sets -h

Documentation
-------------

The different commands are documented in their application groups to give
a better overview of the processes. Every page shows the actual command to
invoke the program, some additional context and optional examples, and an
automatically generated view of the ``--help`` page of the command.
