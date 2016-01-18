import argparse
import logging

from .app import Statuses

log = logging.getLogger(__name__)


def includeme(config):
    config.setdefault('cmd', {})
    config['cmd']['parser'] = parser = argparse.ArgumentParser()
    config['cmd']['subparsers'] = parser.add_subparsers(dest='cmd')
    config.include(conf_help)

    config.include_deferred(parse_args)


def conf_help(config):
    subparsers = config['cmd']['subparsers']
    parser_help = subparsers.add_parser('help', help="Print this help")
    parser_help.set_defaults(cmd_func=run_help)
    config['cmd']['parser_help'] = parser_help


def run_help(app, loop):
    app['cmd']['parser'].print_help()  # pragma no cover


def parse_args(config):
    config['cmd']['args'] = config['cmd']['parser'].parse_args()


def run(app, loop):
    """ Run configured application with command arguments
    """
    if app.status != Statuses.Ok:
        raise ValueError("bad application status: {!r}".format(app.status))

    args = app['cmd']['args']

    if 'cmd_func' in args:
        try:
            args.cmd_func(app, loop)
        finally:
            log.debug("finishing application")
            loop.run_until_complete(app.finish())
            log.debug("closing loop")
            loop.close()
    else:
        run_help(app, loop)
