import os
import tempfile
from unittest.mock import patch

import pytest


@pytest.yield_fixture(scope='module')
def settings_ini():
    data = '''\
[app]
loglevel = "INFO"
'''
    with tempfile.TemporaryDirectory() as tmpdir:
        ini = os.path.join(tmpdir, 'test.ini')
        with open(ini, 'w') as f:
            f.write(data)

        yield ini
        os.remove(ini)


def test_generic(app, loop):
    with app.configure(loop=loop) as config:
        assert 'loglevel' not in config
        config.include('aiotraversal.logger', loglevel="DEBUG")
        config['settings']['loglevel'] = 'INFO'
        assert config['loglevel'] is "DEBUG"

    assert config['loglevel'] == 'INFO'


def test_cmd(app, loop):
    argv = ['cmd', '--loglevel', 'WARNING']

    with patch('sys.argv', new=argv):
        with app.configure(loop=loop) as config:
            assert 'loglevel' not in config
            config.include('aiotraversal.cmd')
            config.include('aiotraversal.logger', loglevel="DEBUG")
            config['settings']['loglevel'] = 'INFO'
            assert config['loglevel'] == 'WARNING'

    assert config['loglevel'] == 'INFO'


def test_settings(app, loop, settings_ini):
    argv = ['cmd', '--settings', settings_ini]

    with patch('sys.argv', new=argv):
        with app.configure(loop=loop) as config:
            assert 'loglevel' not in config
            config.include('aiotraversal.cmd')
            config.include('aiotraversal.settings')
            config.include('aiotraversal.logger', loglevel="DEBUG")
            assert config['loglevel'] == 'DEBUG'

    assert config['loglevel'] == 'INFO'
