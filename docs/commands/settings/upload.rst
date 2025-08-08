Uploading
=========

Once a config file is created (either manually, or saved from the instrument),
the parameters can be uploaded back to the instrument. The config file must
have a valid structure, or the upload will be refused.

The config file can either be in JSON, YAML or TOML format, but regardless,
the structure must follow the required schema.

.. note::
 
    Configs can be validated before upload with the validation command.

Requirements
------------

- GeoCom capable instrument

or

- GSI Online DNA capable instrument

Examples
--------

.. code-block:: json
    :caption: Total station ATR and target setting

    {
        "protocol": "geocom",
        "settings": [
            {
                "subsystem": "aut",
                "options": {
                    "atr": true
                }
            },
            {
                "subsystem": "bap",
                "options": {
                    "target_type": "REFLECTOR",
                    "prizm_type": "MINI"
                }
            }
        ]
    }


.. code-block:: json
    :caption: DNA normal staff direction with meter units

    {
        "protocol": "gsidna",
        "settings": [
            {
                "subsystem": "settings",
                "options": {
                    "distance_unit": "METER",
                    "staff_mode": false
                }
            }
        ]
    }

Usage
-----

.. click:: instrumentman.settings:cli_upload
    :prog: iman upload settings
