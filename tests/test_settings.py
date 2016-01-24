from datetime import timedelta
import os
import tempfile
from unittest.mock import patch

import pytest


@pytest.yield_fixture(scope='module')
def settings_ini():
    data = '''\
[app]
a = true
my-name = "ZZZ"

[serve]
static = "setting"
timeout = 1m
'''
    with tempfile.TemporaryDirectory() as tmpdir:
        ini = os.path.join(tmpdir, 'test.ini')
        with open(ini, 'w') as f:
            f.write(data)

        yield ini
        os.remove(ini)


def test_defaults(app, loop):
    with app.configure(loop=loop) as config:
        config.include('aiotraversal.settings')
        app['settings_ini']['app']['a'] = False
        app['settings_ini']['serve']['b'] = 13

    assert app['settings']['a'] is False
    assert app['settings']['serve']['b'] == 13


def test_file(app, loop, settings_ini):
    with app.configure(loop=loop) as config:
        config.include('aiotraversal.settings')
        app['settings']['file'] = settings_ini
        app['settings_ini']['app']['a'] = False
        app['settings_ini']['serve']['b'] = 13

    assert app['settings']['a'] is True
    assert app['settings']['my-name'] == "ZZZ"

    assert 'serve' in app['settings']
    assert app['settings']['serve']['static'] == 'setting'
    assert app['settings']['serve']['timeout'] == timedelta(minutes=1)
    assert app['settings']['serve']['b'] == 13


def test_with_cmd(app, loop, settings_ini):
    argv = ['cmd', '--settings', settings_ini, 'serve', '--static', 'test']

    with patch('sys.argv', new=argv):
        with app.configure(loop=loop) as config:
            config.include('aiotraversal.cmd')
            config.include('aiotraversal.settings')
            config.include('aiotraversal.serve')

    assert app['settings']['a'] is True
    assert app['settings']['my-name'] == "ZZZ"

    assert 'serve' in app['settings']
    assert app['settings']['serve']['static'] == 'test'
    assert app['settings']['serve']['timeout'] == timedelta(minutes=1)
