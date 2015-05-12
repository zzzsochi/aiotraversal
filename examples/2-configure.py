import asyncio

from aiohttp.web import Response

from aiotraversal import Application
from aiotraversal.resources import Root
from aiotraversal.views import View, RESTView


class HelloView(View):
    @asyncio.coroutine
    def __call__(self):
        return Response(text="Hello World!")


class HelloJSON(RESTView):
    methods = {'get'}

    @asyncio.coroutine
    def get(self):
        return dict(text="Hello World!")


def config_root(app):
    app.bind_view(Root, HelloView)  # add view for '/'
    app.include(config_json)  # include subconfig


def config_json(app):
    app.bind_view(Root, HelloJSON, 'json')  # add view for '/json'


def main():
    loop = asyncio.get_event_loop()

    app = Application()  # create main application instance
    app.include(config_root)  # include config, may be string doted path
    app.start(loop)  # start application

    try:
        loop.run_forever()  # run event loop
    finally:
        loop.close()


if __name__ == '__main__':
    main()
