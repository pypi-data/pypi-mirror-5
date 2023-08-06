GlesPy Package Documentation
============================

This package is just command line bindings for
`GLESP <http://www.glesp.nbi.dk/>`__:

Installation
------------

Requirements
~~~~~~~~~~~~

-  `GLESP <http://www.glesp.nbi.dk/>`__ must be installed with all
   dependences for normal work;
-  `eog <https://projects.gnome.org/eog/>`__ package: to show maps.

Installation
~~~~~~~~~~~~

To install package just input to command line:

::

    pip install glespy

Using
-----

TODO: write this

Features
--------

Automated parameters control, i.e.:

::

    lmin >= 0
    lmax >= lmin
    nx >= lmax * 2 + 1
    np >= nx * 2

PixelMap
~~~~~~~~

...

Alm
~~~

...

PointSource
~~~~~~~~~~~

...

Properties
~~~~~~~~~~

Mutipoled
^^^^^^^^^

...

Rendered
^^^^^^^^

...

Changes
-------

0.1.6
~~~~~

-  quick update alm lmax and lmin
-  temp maps and alm\`s autoremove
-  pointsource can be made of asci file from/for pixelmap
-  python2.6 particle compatibility

