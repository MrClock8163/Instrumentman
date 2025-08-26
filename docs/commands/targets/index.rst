:icon: material/target

Targets
=======

To run a point measurement program, the targets first must be defined. This is
done in JSON format, providing the point IDs, prism types and their 3D
coordinates in an arbitrary coordinate system. This application provides ways
to create such a definition.

.. note::

    A station setup and orientation must be in the same system as the
    targets. If there is no predefined coordinate system, an arbitrary
    local, station centered setup can be used as well.

.. toctree::
    :maxdepth: 1

    measure
    from_csv
    to_csv
    from_gsi
    to_gsi
