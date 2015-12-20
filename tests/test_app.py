import asyncio
from unittest.mock import Mock
import warnings

import pytest

from aiohttp_traversal.ext.resources import Root
from aiotraversal.app import Application, _AiotraversalIncluderWrapper


@pytest.fixture
def loop():
    asyncio.set_event_loop(None)
    return asyncio.new_event_loop()


@pytest.fixture
def app(loop):
    return Application(loop=loop)


def test_init(loop):
    app = Application(loop=loop)
    assert 'settings' in app
    assert 'host' in app['settings']
    assert 'port' in app['settings']
    assert isinstance(app.middlewares, list)
    assert len(app.middlewares) == 1  # aiohttp_exc_handlers


def test_start(loop, app):
    srv = app.start(loop)

    assert isinstance(app.middlewares, tuple)
    assert len(app.middlewares) == 1  # aiohttp_exc_handlers
    assert srv._loop is loop
    assert srv.sockets


def test_include__func(app):
    func = Mock(name='func')
    app.include(func)

    assert func.call_count == 1
    assert len(func.call_args[0]) == 1

    wrapper = func.call_args[0][0]
    assert isinstance(wrapper, _AiotraversalIncluderWrapper)
    assert wrapper._include_object is app
    assert wrapper._include_module == func.__module__


def test_include__str_includeme(app):
    app.include('tests.for_include')
    name, wrapper = app['test_include_info']

    assert name == 'includeme'
    assert isinstance(wrapper, _AiotraversalIncluderWrapper)


def test_include__str_func(app):
    app.include('tests.for_include.func')
    name, wrapper = app['test_include_info']

    assert name == 'func'
    assert isinstance(wrapper, _AiotraversalIncluderWrapper)


def test_include__str_not_callable(app):
    with pytest.raises(TypeError):
        app.include('tests.for_include.not_callable')


def test_include__str_error(app):
    with pytest.raises(ImportError):
        app.include('tests.for_include.not_exists')


def test_include__str_error_includeme(app):
    with pytest.raises(ImportError):
        app.include('tests.for_include.helpers')


def test_include__deeper(app):
    app.include('tests.for_include')
    name, wrapper = app['test_include_info']
    assert name == 'includeme'
    assert isinstance(wrapper, _AiotraversalIncluderWrapper)

    wrapper.include('.func')
    name, wrapper = app['test_include_info']
    assert name == 'func'
    assert isinstance(wrapper, _AiotraversalIncluderWrapper)


def test_add_method(app):
    def func(app, *args, **kwargs):
        return (app, args, kwargs)

    app.add_method('meth', func)
    assert app.meth(1, b=2) == (app, (1,), {'b': 2})


def test_add_method__twice(app):
    def func_1(app):
        return 1

    def func_2(app):
        return 2

    app.add_method('meth', func_1)

    with warnings.catch_warnings(record=True) as w:
        app.add_method('meth', func_2)
        assert len(w) == 1

    assert app.meth() == 2


def test_bind_view__resource(app):
    class Res:
        pass

    def view(request, resource, tail):
        return 'response'

    app.bind_view(Res, view)
    assert Res in app.router.resources


def test_bind_view__exception(app):
    class Exc(Exception):
        pass

    def view(request, exc):
        return 'response'

    app.bind_view(Exc, view)
    assert Exc in app['exc_handlers']


def test_bind_view__exception_w_tail(app):
    class Exc(Exception):
        pass

    def view(request, exc):
        return 'response'

    with pytest.raises(TypeError):
        app.bind_view(Exc, view, '/a/b/c')


def test_get_root(app):
    root = app.get_root()
    assert isinstance(root, Root)
    assert root.app is app
