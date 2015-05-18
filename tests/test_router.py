from unittest.mock import Mock, patch

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from aiotraversal.exceptions import ViewNotResolved
from aiotraversal.router import Router, MatchInfo
from aiotraversal.traversal import (
    find_root,
    lineage,
)

from .helpers import *


@pytest.fixture
def app(root):
    app = Mock(name='app')
    app.get_root.return_value = root
    return app


@pytest.fixture
def router(app):
    return Router(app)


def test_traverse(loop, root, router):
    request = Mock(name='request')
    request.path = '/a/b/c'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert res.name == 'c'
    assert not tail
    assert len(list(lineage(res))) == 4
    assert find_root(res) is root


def test_traverse_with_tail(loop, root, router):
    request = Mock(name='request')
    request.path = '/a/b/not/c'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert res.name == 'b'
    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 3
    assert find_root(res) is root


def test_traverse_root_with_tail(loop, root, router):
    request = Mock(name='request')
    request.path = '/not/c'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 1
    assert res is root


def test_resolve(loop, app, router):
    app.resolve_view.return_value = 'view'
    request = Mock(name='request')
    request.path = '/a/b/not/c'

    with patch('aiotraversal.traversal.traverse') as traverse:
        mi = loop.run_until_complete(router.resolve(request))

    assert not traverse.called
    assert isinstance(mi, MatchInfo)
    assert mi._view == 'view'


def test_resolve_not_found(loop, app, router):
    class VNRMockException(ViewNotResolved):
        def __init__(self):
            pass

    app.resolve_view.side_effect = VNRMockException
    request = Mock(name='request')
    request.path = '/a/b/not/c'

    with pytest.raises(HTTPNotFound):
        loop.run_until_complete(router.resolve(request))
