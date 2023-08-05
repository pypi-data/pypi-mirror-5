pyramid-filterwarnings
======================

Getting Started
---------------

The aim is to provide a generic way to configure the Python warnings.filterwarnings_.


.. _warnings.filterwarnings: _http://docs.python.org/2/library/warnings.html#warnings.filterwarnings

Configuration
-------------

Load the pyramid-filterwarnings plugin from your Pyramid ini file then configure
the level.

::
pyramid.includes =
    ... your other plugins ...
    pyramid_filterwarnings

filterwarnings.level = error

