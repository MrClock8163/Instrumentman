Downloading
===========

The settings are saved by iterating over a set collection of parameter names.
Any particular instrument might not respond to the query of any of the
parameters (e.g. a total station will not respond to queries regarding the
digital level settings). These settings are marked empty, and later cleaned up
before the config file is saved to disk.

It is possible to save the default values for the parameters, that the
instrument did not respond to. In this case, the config file might need to be
manually cleaned of the irrelevant or unwanted settings.

Requirements
------------

- GeoCom capable instrument

or

- GSI Online DNA capable instrument

Examples
--------

.. code-block:: shell
    :caption: Saving only applicable GeoCom settings

    iman download settings COM1 geocom tps_settings.json

.. code-block:: shell
    :caption: Saving to YAML format in a file without extension

    iman download settings -f yaml COM1 geocom tps_settings

.. code-block:: shell
    :caption: Saving all settings including defaults of not applicable ones

    iman download settings --defaults COM1 geocom tps_settings.json

Usage
-----

.. click:: instrumentman.settings:cli_download
    :prog: iman download settings
