import logging
import signal

from .app import Statuses
from .helpers import parse_uri, URI

log = logging.getLogger(__name__)


def includeme(config):
    subparsers = config['cmd']['subparsers']
    parser_serve = subparsers.add_parser('serve', help="Start web server")
    config['cmd']['parser_serve'] = parser_serve

    parser_serve.set_defaults(func=run_serve)

    parser_serve.add_argument('--listen',
                              metavar='HOST:PORT',
                              help="host and port for listen (default 'localhost:8080')")

    parser_serve.add_argument('--static',
                              metavar='DIR',
                              help='Serve static files')

    config['settings'].setdefault('serve', {})

    if 'settings_ini' in config:
        config['settings_ini']['serve']['listen'] = 'localhost:8080'

    config.include_deferred(setup_listen)
    config.include_deferred(setup_static)


def setup_listen(config):
    args = config['cmd']['args']
    if 'serve' in args and 'listen' in args.serve and args.serve.listen:
        config['settings']['serve']['listen'] = args.serve.listen

    listen = config['settings']['serve'].get('listen', '')
    uri = parse_uri(listen, 'localhost:8080')

    config.setdefault('http', {})
    config['http']['host'] = uri.host
    config['http']['port'] = uri.port


def setup_static(config):
    path = config['settings']['serve'].get('static')
    if path is not None:
        config.include('aiotraversal.static')
        config.add_static('aiohttp_traversal.ext.resources.Root',
                          'static', path)


def start_listening(app, loop):
    if app.status != Statuses.Ok:
        raise ValueError("bad application status: {!r}"
                         "".format(app.status))

    app.setdefault('http', {})
    host = app['http'].setdefault('host', 'localhost')
    port = app['http'].setdefault('port', 8080)

    handler = app.make_handler()
    fut = loop.create_server(handler, host, port)
    server = loop.run_until_complete(fut)
    log.info("listening - {}:{}".format(host, port))

    return handler, server


def run_serve(app, loop):  # pragma: no cover
    for signame in ['SIGINT', 'SIGTERM']:
        loop.add_signal_handler(getattr(signal, signame), loop.stop)

    handler, server = start_listening(app, loop=loop)

    loop.run_forever()

    log.debug("stopping serve")
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.run_until_complete(handler.finish_connections(5.0))
