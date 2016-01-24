.. _aiotraversal.serve:

============
Serve helper
============

For add command serving, include ``aiotraversal.serve``:

.. code:: python

    import asyncio

    from aiotraversal import Application
    from aiotraversal.cmd import run

    def main():
        loop = asyncio.get_event_loop()
        app = Application()  # create main application instance

        with app.configure(loop=loop) as config:
            config.include('aiotraversal.cmd')
            config.include('aiotraversal.serve')  # include module for serving
            # some other includes

        run(app, loop=loop)  # start application

.. code:: bash

    $ python app.py serve --help
    usage: app.py serve [-h] [--listen HOST:PORT] [--static DIR]

    optional arguments:
      -h, --help          show this help message and exit
      --listen HOST:PORT  host and port for listen (default 'localhost:8080')
      --static DIR        Serve static files


Objects
=======

* ``config['cmd']['parser_serve']``: subparser for ``serve`` command;


Arguments
=========

``serve`` command have some arguments.

``--listen``
------------

Adderss for listen. Default ``localhost:8080``.

Host or port may be not specified. E.g.:

*  ``--listen 0.0.0.0`` equal ``--listen 0.0.0.0:8080``
*  ``--listen :8082`` equal ``--listen localhost:8082``

``--static``
------------

Serve static directory.
Specified directory is can be found in ``GET /static/``.

.. warning::

    Do not use in production! Access to files is synchronous!


Settings
========

If :ref:`aiotraversal.settings <aiotraversal.settings>` is included, you can use settings for setup default values.

For example:

.. code:: ini

    [serve]
    listen = "10.0.0.15:8080"
    static = "/srv/static"
