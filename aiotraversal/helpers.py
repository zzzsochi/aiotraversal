from collections import namedtuple
import re

URI = namedtuple('URI', ('host', 'port', 'path'))
RE_URI = re.compile(r'^(?P<host>[\w\.]+)?(?::(?P<port>\d+))?(?:\/(?P<path>.+))?$')


def parse_uri(raw, default=URI(None, None, None)):
    if isinstance(default, str):
        default = parse_uri(default)

    res = RE_URI.match(raw)

    if not res:
        raise ValueError("bad uri: {!r}".format(raw))

    groups = res.groupdict()

    host = groups['host'] if groups['host'] is not None else default.host
    port = groups['port'] if groups['port'] is not None else default.port
    path = groups['path'] if groups['path'] is not None else default.path

    if port:
        port = int(port)

    return URI(host, port, path)


def uri_argument(default=None):
    if default:
        default = parse_uri(default)
    else:
        default = URI(None, None, None)

    return lambda raw, default=default: parse_uri(raw, default)
