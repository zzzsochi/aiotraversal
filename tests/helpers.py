import asyncio

import pytest

from aiotraversal.traversal import Traverser

__all__ = ['loop', 'root', 'Resource']


@pytest.fixture
def loop():
    asyncio.set_event_loop(None)
    return asyncio.new_event_loop()


@pytest.fixture
def root():
    return Resource(parent=None, name='ROOT')


class Resource():
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __getitem__(self, name):
        return Traverser(self, (name,))

    @asyncio.coroutine
    def __getchild__(self, name):
        if name == 'not':
            return None
        else:
            return Resource(self, name)

    def __repr__(self):
        return '<resource {!r}>'.format(self.name)
