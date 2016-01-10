from collections import namedtuple
import re

URI = namedtuple('URI', ('host', 'port', 'path'))


def parse_uri(raw, default=URI(None, None, None)):
    res = re.match(r'([\w\.]+)(?::(\w+))?(?:\/(.+))?', raw)

    if not res:
        raise ValueError(raw)

    host, port, path = res.groups()

    if not host:
        host = default.host

    if port:
        port = int(port)
    else:
        port = default.port

    if not path:
        path = default.path

    return URI(host, port, path)


def uri_argument(default=None):
    if default:
        default = parse_uri(default)
    else:
        default = URI(None, None, None)

    return lambda raw, default=default: parse_uri(raw, default)
