import asyncio

import pytest

from aiotraversal.app import Application


@pytest.fixture
def loop():
    asyncio.set_event_loop(None)
    return asyncio.new_event_loop()


@pytest.fixture
def app(loop):
    return Application(loop=loop)
