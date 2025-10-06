Processing
==========

.. caution::
    :class: warning

    The panorama image processing requires extra dependencies.

    - opencv-python

    Install them manually, or install instrumentman with the 'panorama' extra:

    .. code-block:: shell
        
        python -m pip install instrumentman[panorama]

The processing command can be used to merge individual frames of a panorama
capture into a single image, and optionally annotate points on it.

The accuracy of the annotation is usually a few centimeters.

Requirements
------------

- Image metadata JSON file
- Images downloaded from the instrument

Examples
--------

.. code-block:: shell
    :caption: Merging images

    iman process panorama metadata.json merged_panorama.jpg panorama*.jpg


.. code-block:: shell
    :caption: Merging images and annotating points

    iman process panorama --annotate points.csv --fontsize 50 metadata.json merged_panorama.jpg panorama*.jpg

.. code-block:: shell
    :caption: Merging full sphere panorama with downscaling to fit into OpenCV limits

    iman process panorama --scale 2000 metadata.json merged_panorama.jpg panorama*.jpg

.. code-block:: text
    :caption: Example points file for annotations (with the optional label column present)

    P0001,1.0,1.0,0.0,BENCHMARK
    P0002,1.0,2.0,1.0,BENCHMARK
    P0003,1.0,2.0,3.0,TOPO

Usage
-----

.. click:: instrumentman.panorama:cli_calc
    :prog: iman process panorama
