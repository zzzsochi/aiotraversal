from unittest.mock import Mock, MagicMock
import asyncio

import pytest

from aiotraversal.traversal import Traverser
from aiotraversal.resources import (
    Resource,
    InitCoroMixin,
    Root,
)

from .helpers import *


def test_Resource_init():
    parent = Mock(name='parent')
    parent.request.app = MagicMock(name='app')
    parent.app = parent.request.app
    name = 'name'

    res = Resource(parent, name)

    assert res.name == name
    assert res.parent is parent
    assert res.request is parent.request
    assert res.app is parent.request.app
    assert res.setup is res.app['resources'].get(Resource)


def test_Resource_init__root():
    name = 'root'

    res = Resource(None, name)

    assert res.name == name
    assert res.parent is None
    assert res.request is None
    assert res.app is None
    assert res.setup is None


@pytest.fixture
def res_simple():
    parent = Mock(name='parent')
    parent.request.app = MagicMock(name='app')
    parent.app = parent.request.app
    name = 'name'

    return Resource(parent, name)


def test_Resource_getitem(loop, res_simple):
    traverser = res_simple['a']
    assert isinstance(traverser, Traverser)
    assert traverser.resource is res_simple
    assert traverser.path == ('a',)


def test_Resource_getchild(loop, res_simple):
    assert loop.run_until_complete(res_simple.__getchild__('a')) is None


def test_InitCoroMixin(loop):
    class Res(InitCoroMixin, Resource):
        calls_init = 0
        calls_init_coro = 0

        def __init__(self, parent, name):
            super().__init__(parent, name)
            self.calls_init += 1

        @asyncio.coroutine
        def __init_coro__(self):
            self.calls_init_coro += 1

    coro = Res(None, 'name')

    assert asyncio.iscoroutine(coro)

    res = loop.run_until_complete(coro)

    assert isinstance(res, Res)
    assert res.calls_init == 1
    assert res.calls_init_coro == 1


def test_DispatchResource(loop, app):
    class Res(Resource):
        pass

    class CoroRes(InitCoroMixin, Resource):
        calls_init_coro = 0

        @asyncio.coroutine
        def __init_coro__(self):
            self.calls_init_coro += 1

    app.include('aiotraversal.resources')
    app.add_child('aiotraversal.resources.Root', 'simple', Res)
    app.add_child(Root, 'coro', CoroRes)

    request = MagicMock(name='request')
    request.app = app

    root = Root(request)

    res_simple = loop.run_until_complete(iter(root['simple']))
    assert isinstance(res_simple, Res)
    assert res_simple.name == 'simple'
    assert res_simple.parent is root

    res_coro = loop.run_until_complete(iter(root['coro']))
    assert isinstance(res_coro, CoroRes)
    assert res_coro.name == 'coro'
    assert res_coro.parent is root
    assert res_coro.calls_init_coro == 1

    with pytest.raises(KeyError):
        loop.run_until_complete(iter(root['not_exist']))
