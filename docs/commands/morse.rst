:icon: material/volume-high

Morse
=====

The Morse application is a (admittedly not very useful) demo program, that
relays a Morse encoded ASCII message through the speakers of a total station.
The signals are played with the man-machine interface beep signals of the
instrument.

Requirements
------------

- GeoCom capable instrument

Examples
--------

.. code-block:: shell
    :caption: Morse on a TPS100 instrument

    iman morse -c TPS1000 COM1 "Old instrument"

.. code-block:: shell
    :caption: Slower and quieter

    iman morse -u 500 -i 20 COM1 "Slow and quiet"

Usage
-----

.. click:: instrumentman.morse:cli
    :prog: iman morse
