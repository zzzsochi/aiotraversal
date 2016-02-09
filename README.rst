==========================================
Traversal based asynchronous web framework
==========================================

.. image:: https://api.travis-ci.org/zzzsochi/aiotraversal.svg
  :target:  https://secure.travis-ci.org/zzzsochi/aiotraversal
  :alt: CI

.. image:: https://coveralls.io/repos/zzzsochi/aiotraversal/badge.svg
  :target:  https://coveralls.io/r/zzzsochi/aiotraversal
  :alt: Code coverage

.. image:: https://readthedocs.org/projects/aiotraversal/badge/?version=latest
  :target: https://aiotraversal.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status


This is framework, around `aiohttp_traversal <https://github.com/zzzsochi/aiohttp_traversal>`_.

-------
Install
-------

.. code:: shell

    $ pip install aiotraversal

-----
Tests
-----

.. code:: shell

    $ git clone https://github.com/zzzsochi/aiotraversal.git
    $ cd aiotraversal
    $ pip install pytest pytest-cov
    $ py.test --cov ./aiotraversal --cov-report term-missing


--------
Examples
--------

.. code:: shell

    $ git clone https://github.com/zzzsochi/aiotraversal.git
    $ cd aiotraversal
    $ pip install -e .
    $ python3 examples/1-hello.py serve

.. code:: shell

    $ curl http://localhost:8080
    Hello World!
    $ curl http://localhost:8080/json
    {"text": "Hello World!"}

-------
CHANGES
-------

0.9.1 (2016-02-09)
------------------

* Update for new aiohttp;
* Remove ``Configure.register_on_finish`` (fuck b/c!);
* Add ``Configure.on_cleanup`` list for serial cleanup process;
* Fix bug in ``Configure.bind_view`` witn exceptions.


0.9.0 (2016-01-24)
------------------

* Start `documentation <https://aiotraversal.readthedocs.org/en/latest/>`_
* Add `settings <https://aiotraversal.readthedocs.org/en/latest/settings.html>`_;
* Move ``Application.start`` to ``aiotraversal.serve.start_listening`` function;
* Refactoring, refactoring, refactoring, refactoring...


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

