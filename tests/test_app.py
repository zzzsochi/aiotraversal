from unittest.mock import Mock
import warnings

import pytest

from aiotraversal.app import Application, _ApplicationIncludeWrapper
from aiotraversal.exceptions import ViewNotResolved

from .helpers import *


@pytest.fixture
def Res():
    return type('res', (), {})


@pytest.fixture
def View():
    class View:
        def __init__(self, resource):
            self.resource = resource

    return View


def test_init(loop):
    app = Application(loop=loop)
    assert 'settings' in app
    assert 'host' in app['settings']
    assert 'port' in app['settings']
    assert 'resources' in app
    assert isinstance(app.middlewares, list)
    assert len(app.middlewares) == 0


def test_start(loop, app):
    srv = app.start(loop)

    assert isinstance(app.middlewares, tuple)
    assert len(app.middlewares) == 0
    assert srv._loop is loop
    assert srv.sockets


def test_include__func(app):
    func = Mock(name='func')
    app.include(func)

    assert func.call_count == 1
    assert len(func.call_args[0]) == 1

    wrapper = func.call_args[0][0]
    assert isinstance(wrapper, _ApplicationIncludeWrapper)
    assert wrapper._app is app
    assert wrapper._module == func.__module__


def test_include__str_includeme(app):
    app.include('tests.for_include')
    name, wrapper = app['test_include_info']

    assert name == 'includeme'
    assert isinstance(wrapper, _ApplicationIncludeWrapper)


def test_include__str_func(app):
    app.include('tests.for_include.func')
    name, wrapper = app['test_include_info']

    assert name == 'func'
    assert isinstance(wrapper, _ApplicationIncludeWrapper)


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
    assert isinstance(wrapper, _ApplicationIncludeWrapper)

    wrapper.include('.func')
    name, wrapper = app['test_include_info']
    assert name == 'func'
    assert isinstance(wrapper, _ApplicationIncludeWrapper)


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


def test_set_root_class(app):
    assert app._root_class
    new_root_class = Mock(name='root')
    app.set_root_class(new_root_class)
    assert app._root_class is new_root_class


def test_get_root(app):
    request = Mock(name='request', app=app)
    root = app.get_root(request)
    assert root.request is request


def test_resolve_view(app, Res, View):
    res = Res()
    tail = ('a', 'b')
    app['resources'][Res] = {'views': {tail: View}}

    view = app.resolve_view(res, tail)

    assert isinstance(view, View)
    assert view.resource is res


def test_resolve_view__asterisk(app, Res, View):
    res = Res()
    app['resources'][Res] = {'views': {'*': View}}

    view = app.resolve_view(res, ('a', 'b'))

    assert isinstance(view, View)
    assert view.resource is res


def test_resolve_view__mro(app, Res, View):
    class SubRes(Res):
        pass

    res = SubRes()
    app['resources'][Res] = {'views': {'*': View}}

    view = app.resolve_view(res, '*')

    assert isinstance(view, View)
    assert view.resource is res


def test_resolve_view__mro_invert(app, Res, View):
    class SubRes(Res):
        pass

    res = Res()
    app['resources'][SubRes] = {'views': {'*': View}}

    with pytest.raises(ViewNotResolved):
        app.resolve_view(res, '*')


def test_resolve_view__not_resolved(app):
    with pytest.raises(ViewNotResolved):
        app.resolve_view(str, ())


def test_bind_view(app, Res, View):
    app.bind_view(Res, View)
    assert app['resources'][Res]['views'][()] is View


def test_bind_view__tail_str(app, Res, View):
    app.bind_view(Res, View, '/a/b')
    assert app['resources'][Res]['views'][('a', 'b')] is View


def test_bind_view__tail_str_asterisk(app, Res, View):
    app.bind_view(Res, View, '*')
    assert app['resources'][Res]['views']['*'] is View


def test_get_resource_setup(app, Res, View):
    tail = ('a', 'b')
    app['resources'][Res] = {'views': {tail: View}}

    setup = app._get_resource_setup(Res)

    assert setup == {'views': {tail: View}}
