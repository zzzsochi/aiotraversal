import pytest

from aiohttp_traversal.ext.resources import Root
from aiotraversal.app import Application, Statuses


def test_init(loop):
    app = Application(loop=loop)
    assert app.status == Statuses.NotConfigured
    assert 'settings' in app
    assert 'host' in app['settings']
    assert 'port' in app['settings']
    assert isinstance(app.middlewares, list)
    assert len(app.middlewares) == 1  # aiohttp_exc_handlers


def test_statuses__ok(loop, app):
    assert app.status == Statuses.NotConfigured

    with app.configure(loop=loop):
        assert app.status == Statuses.Configuring

    assert app.status == Statuses.Ok


def test_statuses__broken(loop, app):
    assert app.status == Statuses.NotConfigured

    class Exc(Exception):
        pass

    try:
        with app.configure(loop=loop):
            assert app.status == Statuses.Configuring
            raise Exc()
    except Exc:
        pass

    assert app.status == Statuses.Broken


def test_statuses__broken_deffered(loop, app):
    assert app.status == Statuses.NotConfigured

    class Exc(Exception):
        pass

    def func(config):
        raise Exc()

    try:
        with app.configure(loop=loop) as config:
            assert app.status == Statuses.Configuring
            config.include_deferred(func)
    except Exc:
        pass

    assert app.status == Statuses.Broken


def test_start(loop, app):
    with app.configure(loop=loop):
        pass

    srv = app.start(loop)

    assert isinstance(app.middlewares, tuple)
    assert len(app.middlewares) == 1  # aiohttp_exc_handlers
    assert srv._loop is loop
    assert srv.sockets


def test_start__error(loop, app):
    try:
        with app.configure(loop=loop):
            raise RuntimeError()
    except RuntimeError:
        pass

    with pytest.raises(ValueError):
        app.start(loop)


def test_get_root(app):
    root = app.get_root()
    assert isinstance(root, Root)
    assert root.app is app
