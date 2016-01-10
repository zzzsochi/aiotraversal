import signal

from .helpers import uri_argument


def includeme(config):
    subparsers = config['cmd']['subparsers']
    parser_serve = subparsers.add_parser('serve', help="Start web server")
    config['cmd']['parser_serve'] = parser_serve

    parser_serve.set_defaults(cmd_func=run_serve, cmd='serve')

    parser_serve.add_argument('--listen',
                              type=uri_argument('localhost:8080'),
                              default='localhost:8080',
                              metavar='HOST:PORT',
                              help="host and port for listen (default 'localhost:8080')")

    parser_serve.add_argument('--static',
                              metavar='DIR',
                              help='Serve static files')

    config.include_deferred(setup_listen)
    config.include_deferred(setup_static)


def setup_listen(config):
    args = config['cmd']['args']

    if getattr(args, 'cmd', '') == 'serve':
        config['settings']['host'] = args.listen.host
        config['settings']['port'] = args.listen.port


def setup_static(config):
    args = config['cmd']['args']

    if getattr(args, 'static', None):
        config.include('aiotraversal.static')
        config.add_static('aiohttp_traversal.ext.resources.Root',
                          'static', args.static)


def run_serve(app, loop):
    app.start(loop=loop)

    for signame in ['SIGINT', 'SIGTERM']:
        loop.add_signal_handler(getattr(signal, signame), loop.stop)

    loop.run_forever()
