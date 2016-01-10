import argparse
import logging


def includeme(config):
    parser = config['cmd']['parser']
    parser.add_argument('--loglevel',
                        choices=['NOTSET', 'DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING',
                        metavar='WARNING',
                        help='Set log level')

    config.include(setup_loglevel)


def setup_loglevel(config):
    """ Monkey patching for setup loglevel before main argument parse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel',
                        choices=['NOTSET', 'DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING',
                        metavar='WARNING',
                        help='Set log level')

    args = parser.parse_known_args()[0]

    loglevel = args.loglevel.upper()
    config['settings']['loglevel'] = loglevel

    if loglevel != 'NOTSET':
        logging.getLogger('asyncio').setLevel('ERROR')
        logging.basicConfig(level=loglevel)
