import argparse
import logging


def includeme(config, loglevel='WARNING'):
    config['settings']['loglevel'] = loglevel
    _setup_loglevel(config, loglevel)

    if 'cmd' in config:
        parser = config['cmd']['parser']
        parser.add_argument('--loglevel',
                            choices=['NOTSET', 'DEBUG', 'INFO',
                                     'WARNING', 'ERROR', 'CRITICAL'],
                            metavar=loglevel,
                            help='Setup logging level')

        config.include(setup_loglevel_from_cmd)

    config.include_deferred(setup_loglevel_from_settings)


def setup_loglevel_from_cmd(config):
    """ Monkey patching for setup loglevel before main argument parse
    """
    default = config['settings']['loglevel']

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--loglevel',
                        choices=['NOTSET', 'DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        default=default,
                        metavar='WARNING',
                        help='Set log level')

    args = parser.parse_known_args()[0]

    loglevel = getattr(args, 'loglevel', default).upper()
    config['settings']['loglevel'] = loglevel

    if loglevel != config['loglevel']:
        _setup_loglevel(config, loglevel)


def setup_loglevel_from_settings(config):
    loglevel = config['settings']['loglevel'].upper()
    if loglevel != config['loglevel']:
        _setup_loglevel(config, loglevel)


def _setup_loglevel(config, loglevel):
    logging.getLogger('asyncio').setLevel('ERROR')
    logging.basicConfig(level=loglevel)
    config['loglevel'] = loglevel
