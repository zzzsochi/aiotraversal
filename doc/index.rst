============
aiotraversal
============

.. image:: https://api.travis-ci.org/zzzsochi/aiotraversal.svg
  :target:  https://secure.travis-ci.org/zzzsochi/aiotraversal
  :alt: CI

.. image:: https://coveralls.io/repos/zzzsochi/aiotraversal/badge.svg
  :target:  https://coveralls.io/r/zzzsochi/aiotraversal
  :alt: Code coverage

.. image:: https://readthedocs.org/projects/aiotraversal/badge/?version=latest
  :target: https://aiotraversal.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status

Traversal based asynchronous web framework, based on
`aiohttp_traversal <https://github.com/zzzsochi/aiohttp_traversal>`_.


Hello World
===========

``app.py``:

.. code:: python

    import asyncio

    from aiohttp.web import Response

    from aiohttp_traversal.ext.resources import Root
    from aiohttp_traversal.ext.views import View, RESTView

    from aiotraversal import Application
    from aiotraversal.cmd import run


    class HelloView(View):
        @asyncio.coroutine
        def __call__(self):
            return Response(text="Hello World!\n")


    class HelloJSON(RESTView):
        methods = {'get'}

        @asyncio.coroutine
        def get(self):
            return dict(text="Hello World!")


    def main():
        loop = asyncio.get_event_loop()

        app = Application()  # create main application instance

        with app.configure(loop=loop) as config:  # start configure process
            config.include('aiotraversal.cmd')  # include module for command-line parsing
            config.include('aiotraversal.serve')  # include module for start serving
            config.bind_view(Root, HelloView)  # add view for '/'
            config.bind_view(Root, HelloJSON, 'json')  # add view for '/json'

        run(app, loop=loop)  # start application


    if __name__ == '__main__':
        main()

.. code:: bash

    $ python app.py serve

.. code:: bash

    $ curl http://localhost:8080
    Hello World!
    $ curl http://localhost:8080/json
    {"text": "Hello World!"}


Content
=======

.. toctree::
    :maxdepth: 2

    cmd
    logger
    serve
    settings
