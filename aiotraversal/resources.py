import asyncio
import logging

from .abc import AbstractResource
from .traversal import Traverser
from .helpers import resolver

log = logging.getLogger(__name__)


class Resource(AbstractResource):
    parent = None
    name = None
    request = None
    app = None
    setup = None

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

        if parent is not None:
            self.request = parent.request
            self.app = self.request.app
            self.setup = self.app['resources'].get(self.__class__)

    def __getitem__(self, name):
        return Traverser(self, (name,))

    @asyncio.coroutine
    def __getchild__(self, name):
        return None


class InitCoroMixin:
    """ Mixin for create initialization coroutine
    """
    def __new__(cls, *args, **kwargs):
        """ This is magic!
        """
        instance = super().__new__(cls)

        @asyncio.coroutine
        def coro():
            instance.__init__(*args, **kwargs)
            yield from instance.__init_coro__()
            return instance

        return coro()

    @asyncio.coroutine
    def __init_coro__(self):
        raise NotImplementedError


class DispatchMixin:
    @asyncio.coroutine
    def __getchild__(self, name):
        if (self.setup is not None
                and 'children' in self.setup
                and name in self.setup['children']):

            res = self.setup['children'][name](self, name)

            if asyncio.iscoroutine(res):
                return (yield from res)
            else:
                return res
        else:
            return None


class DispatchResource(DispatchMixin, Resource):
    pass


class Root(DispatchResource):
    def __init__(self, request):
        super().__init__(parent=None, name=None)
        self.request = request
        self.app = self.request.app
        self.setup = self.app['resources'].get(self.__class__)


@resolver('parent', 'child')
def add_child(app, parent, name, child):
    """ Add child resource for dispatch-resources
    """
    parent_setup = app._get_resource_setup(parent)
    parent_setup.setdefault('children', {})[name] = child


def includeme(app):
    app.add_method('add_child', add_child)
