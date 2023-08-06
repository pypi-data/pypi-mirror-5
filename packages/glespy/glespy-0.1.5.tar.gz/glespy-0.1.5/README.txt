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
-  `eog <https://projects.gnome.org/eog/>`__ package.

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

0.1.5
~~~~~

-  added Angle class to ext:
-  checking of existence of files
-  map rotation
-  getting top or bottom of map
-  basic arithmetics on maps
-  map masking
-  bugs fixes

0.1.3
~~~~~

-  rotate alm by dphi, dtheta, dpsi

It\`s appeared! :)
