import asyncio
import logging

from aiohttp.abc import AbstractRouter, AbstractMatchInfo
from aiohttp.web_exceptions import HTTPNotFound

from .traversal import traverse

log = logging.getLogger(__name__)


class MatchInfo(AbstractMatchInfo):
    def __init__(self, view):
        self._view = view

    def handler(self, request):
        return self._view()

    @property
    def route(self):
        pass


class Router(AbstractRouter):
    def __init__(self, app):
        self.app = app

    @asyncio.coroutine
    def resolve(self, request):
        resource, tail = yield from self.traverse(request)
        request.resource = resource
        request.tail = tail
        view = self.get_view(resource, tail)

        return MatchInfo(view)

    @asyncio.coroutine
    def traverse(self, request):
        path = tuple(p for p in request.path.split('/') if p)
        root = self.app.get_root(request)

        if path:
            return (yield from traverse(root, path))
        else:
            return root, path

    def get_view(self, resource, tail=()):
        resource_class = resource.__class__

        for rc in resource_class.__mro__[:-1]:
            if rc in self.app['resources']:
                views = self.app['resources'][rc]['views']

                if tail in views:
                    view = views[tail]
                    break

                elif '*' in views:
                    view = views['*']
                    break

        else:
            raise HTTPNotFound

        return view(resource)
