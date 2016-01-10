import asyncio
from collections import abc
import enum
from types import MethodType
import warnings
import logging

from aiohttp.web import Application as BaseApplication
from aiohttp_traversal import TraversalRouter
from aiohttp_traversal.ext.resources import add_child
from aiohttp_exc_handlers import exc_handlers_middleware, bind_exc_handler

import includer
from resolver_deco import resolver


log = logging.getLogger(__name__)


class Statuses(enum.Enum):
    """ Application's statuses
    """
    NotConfigured = 1
    Configuring = 2
    Broken = 3
    Ok = 4
    Finishing = 5
    Finished = 6


class _ConfigureIncluderMixin(includer.IncluderMixin):
    def _includer_get_wrapper(self, include_module):
        return _ConfigureIncluderWrapper(self, include_module)

    @property
    def __package_for_resolve_deco__(self):
        return self._include_module


class _ConfigureIncluderWrapper(_ConfigureIncluderMixin,
                                includer._IncluderWrapper):
    pass


class Configure(_ConfigureIncluderMixin, abc.MutableMapping):
    """ Configure object for application
    """
    active = False

    def __init__(self, app, loop):
        if app.status != Statuses.NotConfigured:
            raise ValueError("bad application status: {!r}"
                             "".format(app.status))
        self.app = app
        self.loop = loop

    def __enter__(self):
        self.active = True
        self.app.status = Statuses.Configuring

        self.add_method('add_child', add_child)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        if exc_type is not None:
            self.app.status = Statuses.Broken
        else:
            self.app.status = Statuses.Ok

    def __getitem__(self, key):
        return self.app[key]

    def __setitem__(self, key, value):
        self.app[key] = value

    def __delitem__(self, key):
        del self.app[key]

    def __iter__(self):
        return iter(self.app)

    def __len__(self):
        return len(self.app)

    @property
    def _middlewares(self):
        return self.app._middlewares

    @property
    def middlewares(self):
        return self._middlewares

    @property
    def router(self):
        return self.app.router

    @resolver('func')
    def add_method(self, name, func):
        """ Add method to application

        Usage from configuration process.
        """
        if not self.active:
            raise RuntimeError("configure process is not active")

        if not isinstance(name, str):
            raise TypeError("name is not a string!")

        config = getattr(self, '_config', self)

        if hasattr(config, name):
            warnings.warn("Method {} is already exist, replacing it"
                          "".format(name))

        meth = MethodType(func, config)
        setattr(config, name, meth)

    @resolver('resource', 'view')
    def bind_view(self, resource, view, tail=()):
        """ Bind view to resource
        """
        if not self.active:
            raise RuntimeError("configure process is not active")

        log.debug("bind_view({!r}, {!r}, {!r}, {!r})"
                  "".format(self, resource, view, tail))

        if issubclass(resource, Exception):
            if tail:
                raise TypeError("tail not accepted for exception resources")

            bind_exc_handler(self, resource, view)
        else:
            self.app.router.bind_view(resource, view, tail)


class Application(BaseApplication):
    """ Main application object
    """
    status = Statuses.NotConfigured

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('router', TraversalRouter())
        kwargs.setdefault('middlewares', [exc_handlers_middleware])
        super().__init__(*args, **kwargs)

        self.router.set_root_factory('aiohttp_traversal.ext.resources.Root')

        self._middlewares = list(self._middlewares)  # some monkey patching

        self['settings'] = {}

        self['settings'].setdefault('host', 'localhost')
        self['settings'].setdefault('port', 8080)

    def configure(self, loop):
        return Configure(self, loop)

    def start(self, loop):
        """ Start applisation and add to event loop
        """
        if self.status != Statuses.Ok:
            raise ValueError("bad application status: {!r}"
                             "".format(self.status))

        self._middlewares = tuple(self._middlewares)

        host = self['settings']['host']
        port = self['settings']['port']

        f = loop.create_server(self.make_handler(), host, port)
        srv = loop.run_until_complete(f)
        log.info("listening - {}:{}".format(host, port))
        return srv

    @asyncio.coroutine
    def finish(self):
        self.status = Statuses.Finishing
        yield from super().finish()
        self.status = Statuses.Finished

    def get_root(self, *args, **kwargs):
        """ Return new root of resource tree
        """
        return self.router.get_root(self, *args, **kwargs)
