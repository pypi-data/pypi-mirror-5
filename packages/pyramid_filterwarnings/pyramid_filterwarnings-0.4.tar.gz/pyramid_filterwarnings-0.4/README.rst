pyramid_filterwarnings
======================

Getting Started
---------------

The aim of this project is to provide a generic way to configure python
`warnings.filterwarnings`_.
Python warnings can be configured via Environment variable, Python interpreter
argument, or directly in the code. This plugin provides to Pyramid application
a clean way to configure the warning level via its configuration file.


Configuration
-------------

Set the pyramid_filterwarnings plugin from in the Pyramid ini file then
configure the level.

::

    pyramid.includes =
        pyramid_filterwarnings
        ... your other plugins ...

    # configure the warning level, default is ignore
    filterwarnings.level = ignore

.. note::

    You should set the filterwarnings on top of the configuration if you want
    to catch plugins warnings. You should also set the level to error for your
    developement environment to fix the warning as soon as possible.


It is also possible to set category_, module and message, and do many rules.

::

    # Other optionals configurations keys
    # filterwarnings.category = DeprecationWarning
    # filterwarnings.module = pyramid\..*

    # Add other rules
    filterwarnings.1.category = DeprecationWarning
    filterwarnings.1.module = sqlalchemy\..*
    filterwarnings.1.level = notice

    filterwarnings.2.action = ignore
    filterwarnings.2.module = pyramid_jinja2\.*
    filterwarnings.2.message = reload_templates setting is deprecated

    # and more if necessary...


.. _warnings.filterwarnings: _http://docs.python.org/2/library/warnings.html#warnings.filterwarnings
.. _category: _http://docs.python.org/2/library/warnings.html#warning-categories

