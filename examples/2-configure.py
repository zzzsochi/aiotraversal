"""
More about configure process.
Run sequentially:

    * python 2-configure.py --help
    * python 2-configure.py serve --help
    * python 2-configure.py serve

Create `entry_points` in a `setup.py`.
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


def config_root(config):
    config.bind_view(Root, HelloView)  # add view for '/'
    config.include(config_json)  # include subconfig


def config_json(config):
    config.bind_view(Root, HelloJSON, 'json')  # add view for '/json'


def main():
    loop = asyncio.get_event_loop()

    app = Application()

    with app.configure(loop=loop) as config:
        config.include('aiotraversal.cmd')  # include cmd module
        config.include('aiotraversal.serve')
        config.include(config_root)  # include config, may be string doted path

    run(app, loop)


if __name__ == '__main__':
    main()
