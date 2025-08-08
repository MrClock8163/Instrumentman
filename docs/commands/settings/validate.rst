Validation
==========

An instrument settings file must have a valid structure, or the upload will be
refused. The schema file is available in the
`GitHub repository <https://github.com/MrClock8163/Instrumentman/blob/main/src/instrumentman/settings/schema_settings.json>`_.

Requirements
------------

- Previously saved settings configuration file

Usage
-----

.. click:: instrumentman.settings:cli_validate
    :prog: iman validate settings

