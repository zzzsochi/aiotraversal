import argparse
import logging

from .app import Statuses

log = logging.getLogger(__name__)


def includeme(config):
    config.setdefault('cmd', {})
    config['cmd']['parser'] = parser = ArgumentParser()
    config['cmd']['subparsers'] = parser.add_subparsers(dest='cmd')
    config.include(conf_help)

    config.include_deferred(parse_args)


def conf_help(config):
    subparsers = config['cmd']['subparsers']
    parser_help = subparsers.add_parser('help', help="Print this help")
    parser_help.set_defaults(func=run_help)
    config['cmd']['parser_help'] = parser_help


def run_help(app, loop):
    app['cmd']['parser'].print_help()  # pragma no cover


def parse_args(config):
    args = config['cmd']['args'] = config['cmd']['parser'].parse_args()

    if 'cmd' in args and args.cmd in args:
        config['run_func'] = getattr(getattr(args, args.cmd), 'func', None)
    else:
        config['run_func'] = None  # pragma: no cover


def run(app, loop):
    """ Run configured application with command arguments
    """
    if app.status != Statuses.Ok:  # pragma: no cover
        raise ValueError("bad application status: {!r}".format(app.status))

    if app.get('run_func') is not None:
        try:
            app['run_func'](app, loop)
        finally:
            log.debug("finishing application")
            loop.run_until_complete(app.finish())
            log.debug("closing loop")
            loop.close()
    else:  # pragma: no cover
        run_help(app, loop)


class ArgumentParser(argparse.ArgumentParser):
    def parse_args(self, *args, **kw):
        args = super().parse_args(*args, **kw)

        topdest = [action.dest for action in self._actions]
        subargs = {}
        for key, value in args.__dict__.copy().items():
            if key not in topdest:
                delattr(args, key)
                subargs[key] = value

        setattr(args, args.cmd, argparse.Namespace(**subargs))
        return args
