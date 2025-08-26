Measurement
===========

Once the target definition JSON is created, the measurement sets can
be started. In each measurement session the time, internal temperature
and battery level are recorded at start. For each target the horizontal angle,
zenith angle and slope distance are recorded.

Requirements
------------

- Target definition file (see the Targets application)
- GeoCom capable robotic total station with ATR

Order
-----

The measurement order can have a significant effect on the time it takes to
complete a full cycle. The fastest order of face 1-2 measurement pairs is
``ABba`` or ``ABab``, that involve the smallest number of face changes. Other
orders might be benefitial if the targets cannot be occupied for the duration
of the full cycle. The figure below illustrates the different supported
measurement patterns. The default order is ``ABba``.

.. note::
    
    The measurement order has the most significant effect on overall cycle
    duration with older instruments, where the switch between two faces
    usuallay takes around 5-6 seconds. These small intervals can add up over
    long sets or surveys.

.. image:: order.png
   :width: 400
   :align: center
   :alt: Set measurement order

Results
-------

The results from each session are saved into a separate JSON file. These
can be later merged for processing if necessary.

Scheduling
----------

Periodic measurement sessions can be echieved by settings up a scheduled
task in the scheduler tool of the respective operating system of the
controlling computer (e.g. Task Scheduler on Windows, crontab on Linux).

Examples
--------

.. code-block:: shell
    :caption: Enabling connection retries and timeout recovery attempts (might be useful with bluetooth connections)

    iman measure set -r 3 --sync-after-timeout COM3 targets.json set.json

.. code-block:: shell
    :caption: Measuring to just a subset of the targets

    iman measure set -p P1 -p P2 -p P8 COM3 targets.json set.json

.. code-block:: shell
    :caption: Measuring in face 1 only

    iman measure set -o ABCD COM3 targets.json set.json

.. code-block:: shell
    :caption: Saving results with file name template (useful for scheduled measurements)

    iman measure set COM3 targets.json "set_{date}_{time}.json"

Usage
-----

.. click:: instrumentman.setmeasurement:cli_measure
    :prog: iman measure set
