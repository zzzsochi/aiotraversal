.. _aiotraversal.logger:

============
Setup logger
============

Use ``config.include('aiotraversal.logger')`` for setup logger.

Three stages setup loglevel
===========================

1. At first get loglevel from include keyword:

.. code:: python

    config.include('aiotraversal.logger', loglevel='INFO')

2. Get loglevel from :ref:`command-line argument <aiotraversal.logger/args/settings>` (before general :ref:`argument parsing <aiotraversal.cmd>`);
3. Get loglevel from :ref:`settings <aiotraversal.logger/settings>`;

Objects
=======

* ``app['loglevel']``: current loglevel;

.. * ``app['logger']``: main application logger

Arguments
=========

:ref:`aiotraversal.cmd <aiotraversal.cmd>` module is **not** required.

.. _aiotraversal.logger/args/settings:

``--loglevel``
--------------

Loglevel, who set on second stage.


.. _aiotraversal.logger/settings:

Settings
========

:ref:`aiotraversal.settings <aiotraversal.settings>` module is **not** required,
but if your want use with it, :ref:`settings <aiotraversal.settings>` must include first.

.. code:: ini

    [app]
    logger = "DEBUG"
