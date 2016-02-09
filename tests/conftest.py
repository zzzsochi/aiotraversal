import asyncio

import pytest

from aiotraversal.app import Application


@pytest.yield_fixture(scope='function')
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    asyncio.set_event_loop(None)


@pytest.fixture
def app(loop):
    return Application(loop=loop)
