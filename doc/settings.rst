.. _aiotraversal.settings:

========
Settings
========

Just include :ref:`aiotraversal.settings`.

Settings uses `zini <https://github.com/zzzsochi/zini>`_.

All keys in section named "app", set to ``config['settings']``.
Other sections set to ``config['settings'][section_name]``.

For example:

.. code:: ini

    [app]
    author = "ZZZ"

    [serve]
    listen = ":6543"

.. code:: python

    assert app['settings']['author'] == 'ZZZ'
    assert app['settings']['serve']['listen'] == ':6543'


Objects
=======

* ``config['settings_ini']``: instance of `Zini <https://github.com/zzzsochi/zini>`;
* ``config['settings']['file']``: path to file with settings;


Arguments
=========

:ref:`aiotraversal.cmd <aiotraversal.cmd>` module is **not** required.

``--settings``
--------------

Path to ini-file with setings. This is setup ``config['settings']['file']``.
