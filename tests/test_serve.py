import pytest

from aiotraversal.serve import start_listening


def test_start_listening(loop, app):
    with app.configure(loop=loop):
        pass

    handler, srv = start_listening(app, loop=loop)

    assert srv._loop is loop
    assert srv.sockets


def test_start_listening__error(loop, app):
    try:
        with app.configure(loop=loop):
            raise RuntimeError()
    except RuntimeError:
        pass

    with pytest.raises(ValueError):
        start_listening(app, loop=loop)
