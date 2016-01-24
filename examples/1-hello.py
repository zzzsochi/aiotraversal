"""
Hello World application.

Start:

    python 1-hello.py serve

After start, check urls:

    * http://localhost:8080/
    * http://localhost:8080/json

"""

import asyncio

from aiohttp.web import Response

from aiohttp_traversal.ext.resources import Root
from aiohttp_traversal.ext.views import View, RESTView

from aiotraversal import Application
from aiotraversal.cmd import run


class HelloView(View):
    @asyncio.coroutine
    def __call__(self):
        return Response(text="Hello World!")


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
