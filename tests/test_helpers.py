import pytest

from aiotraversal.helpers import URI, parse_uri, uri_argument


DEFAULT = URI('H', 2, 'P')


@pytest.mark.parametrize(
    'value, default, host, port, path',
    [
        ('h:1/p', None, 'h', 1, 'p'),
        ('h:1', None, 'h', 1, None),
        ('h:1/p', DEFAULT, 'h', 1, 'p'),
        ('h:1', DEFAULT, 'h', 1, 'P'),
        ('h', DEFAULT, 'h', 2, 'P'),
        ('h/p', DEFAULT, 'h', 2, 'p'),
    ]
)
def test_parse_uri(value, default, host, port, path):
    if default is not None:
        uri = parse_uri(value, default)
    else:
        uri = parse_uri(value)

    assert isinstance(uri, URI)
    assert uri.host == host
    assert uri.port == port
    assert uri.path == path


def test_parse_uri__empty():
    assert parse_uri('') == URI(None, None, None)


def test_parse_uri__bad_port():
    with pytest.raises(ValueError):
        parse_uri('h:e/p')


@pytest.mark.parametrize(
    'value, default, host, port, path',
    [
        ('h:1/p', None, 'h', 1, 'p'),
        ('h:1', None, 'h', 1, None),
        ('h:1/p', 'H:2/P', 'h', 1, 'p'),
        ('h:1', 'H:2/P', 'h', 1, 'P'),
        ('h', 'H:2/P', 'h', 2, 'P'),
        ('h/p', 'H:2/P', 'h', 2, 'p'),
    ]
)
def test_uri_argument(value, default, host, port, path):
    func = uri_argument(default)
    assert isinstance(func, type(lambda: None))

    uri = func(value)
    assert isinstance(uri, URI)
    assert uri.host == host
    assert uri.port == port
    assert uri.path == path
