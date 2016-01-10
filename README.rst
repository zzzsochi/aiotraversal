==========================================
Traversal based asyncronious web framework
==========================================

.. image:: https://api.travis-ci.org/zzzsochi/aiotraversal.svg
  :target:  https://secure.travis-ci.org/zzzsochi/aiotraversal
  :align: right

.. image:: https://coveralls.io/repos/zzzsochi/aiotraversal/badge.svg
  :target:  https://coveralls.io/r/zzzsochi/aiotraversal
  :align: right

This is framework, around `aiohttp_traversal <https://github.com/zzzsochi/aiohttp_traversal>`_.

-----
Tests
-----

.. code:: shell

    $ pip install pytest
    $ py.test


CHANGES
=======

0.8.0-dev (2016-01-10)
----------------------

* Started CHANGES;
* New configuration process:

    .. code:: python

    def main():
        loop = asyncio.get_event_loop()
        app = Application()

        with app.configure(loop=loop) as config:
            config.include(func)

        app.start()

    def func(config):
        work_configure()
