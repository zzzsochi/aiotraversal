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
    """ Application's statuses.
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


@asyncio.coroutine
def _aiotraversal_on_cleanup(app):
    for task in app['aiotraversal']['on_cleanup']:
        if asyncio.iscoroutine(task):
            yield from task
        else:
            res = task(app)
            if asyncio.iscoroutine(res):
                yield from res


class Configure(_ConfigureIncluderMixin, abc.MutableMapping):
    """ Configure object for application.
    """
    active = False

    def __init__(self, app, loop):
        if app.status != Statuses.NotConfigured:
            raise ValueError("bad application status: {!r}"
                             "".format(app.status))
        self._app = app
        self._loop = loop
        self._includes_deferred = []

        app.setdefault('aiotraversal', {})
        app['aiotraversal'].setdefault('on_cleanup', [])
        self.app.on_cleanup.insert(0, _aiotraversal_on_cleanup)

    def __enter__(self):
        self.active = True
        self.app.status = Statuses.Configuring

        self.add_method('add_child', add_child)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.app.status = Statuses.Broken
        else:
            try:
                for config, func, kwargs in self._includes_deferred:
                    config.include(func, **kwargs)
            except Exception:
                self.app.status = Statuses.Broken
                raise
            else:
                self.app.status = Statuses.Ok
            finally:
                self.active = False

    def __getitem__(self, key):  # pragma: no cover
        return self.app[key]

    def __setitem__(self, key, value):  # pragma: no cover
        self.app[key] = value

    def __delitem__(self, key):  # pragma: no cover
        del self.app[key]

    def __iter__(self):  # pragma: no cover
        return iter(self.app)

    def __len__(self):  # pragma: no cover
        return len(self.app)

    @property
    def app(self):  # pragma: no cover
        return self._app

    @property
    def loop(self):  # pragma: no cover
        return self._loop

    @property
    def middlewares(self):  # pragma: no cover
        return self.app.middlewares

    @property
    def router(self):
        return self.app.router

    @property
    def on_cleanup(self):
        return self.app['aiotraversal']['on_cleanup']

    def include_deferred(self, func, **kwargs):
        """ Include this on configuration process exit.
        """
        self._includes_deferred.append((self, func, kwargs))

    @resolver('func')
    def add_method(self, name, func):
        """ Add method to application.

        Usage from configuration process.
        """
        if not self.active:
            raise RuntimeError("configure process is not active")

        if not isinstance(name, str):  # pragma: no cover
            raise TypeError("name is not a string!")

        config = getattr(self, '_config', self)

        if hasattr(config, name):
            warnings.warn("Method {} is already exist, replacing it"
                          "".format(name))

        meth = MethodType(func, config)
        setattr(config, name, meth)

    @resolver('resource', 'view')
    def bind_view(self, resource, view, tail=()):
        """ Bind view to resource.
        """
        if not self.active:
            raise RuntimeError("configure process is not active")

        log.debug("bind_view: {mod}, {res}{tail} -> {view}"
                  "".format(
                      mod=self._include_module or '__main__',
                      res=resource.__name__,
                      tail=tail if isinstance(tail, str) else '/'.join(tail),
                      view=view.__name__,
                  ))

        if issubclass(resource, Exception):
            if tail:
                raise TypeError("tail not accepted for exception resources")

            bind_exc_handler(self.app, resource, view)
        else:
            self.app.router.bind_view(resource, view, tail)


class Application(BaseApplication):
    """ Main application object.
    """
    status = Statuses.NotConfigured

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('router', TraversalRouter())
        kwargs.setdefault('middlewares', [exc_handlers_middleware])
        super().__init__(*args, **kwargs)

        self.router.set_root_factory('aiohttp_traversal.ext.resources.Root')

        self['settings'] = {}

    def configure(self, loop):
        return Configure(self, loop)

    @asyncio.coroutine
    def cleanup(self):
        self.status = Statuses.Finishing
        yield from super().cleanup()
        self.status = Statuses.Finished

    def get_root(self, *args, **kwargs):
        """ Return new root of resource tree.
        """
        return self.router.get_root(self, *args, **kwargs)
