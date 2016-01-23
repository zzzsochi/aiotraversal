"""
Hello World application.

After start, check urls:

    * GET localhost:8080/
    * GET localhost:8080/json

"""

import asyncio

from aiohttp.web import Response

from aiohttp_traversal.ext.resources import Root
from aiohttp_traversal.ext.views import View, RESTView

from aiotraversal import Application
from aiotraversal.serve import start_listening


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
        config.bind_view(Root, HelloView)  # add view for '/'
        config.bind_view(Root, HelloJSON, 'json')  # add view for '/json'

    start_listening(app, loop=loop)  # start listening localhost:8080

    try:
        loop.run_forever()  # run event loop
    finally:
        loop.close()


if __name__ == '__main__':
    main()
