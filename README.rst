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

0.9.0 (2016-01-XX)
------------------

* Move ``Application.start`` to ``aiotraversal.serve.start_listening`` function;


0.8.0 (2016-01-10)
------------------

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

* Add ``Configure.include_deferred``;

* Add modules for command line:

    - ``aiotraversal.cmd``;
    - ``aiotraversal.logger``;
    - ``aiotraversal.serve``;

    .. code:: python

        import asyncio

        from aiotraversal import Application
        from aiotraversal.cmd import run

        def main():
            loop = asyncio.get_event_loop()
            app = Application()

            with app.configure(loop=loop) as config:
                config.include('aiotraversal.cmd')
                config.include('aiotraversal.logger')
                config.include('aiotraversal.serve')

            run(app, loop)

        if __name__ == '__main__':
            main()

    .. code:: shell

        $ cmd
        usage: cmd [--loglevel WARNING] {help,serve} ...

        positional arguments:
          {help,serve}
            help              Print this help
            serve             Start web server

        optional arguments:
          --loglevel WARNING  Set log level

        $ cmd --loglevel=DEBUG serve
        INFO:aiotraversal.app:listening - localhost:8080
        ^CDEBUG:aiotraversal.cmd:finishing application
        DEBUG:aiotraversal.cmd:closing loop

