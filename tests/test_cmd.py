from datetime import timedelta
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from aiotraversal.cmd import ArgumentParser, run


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


def test_parser():
    parser = ArgumentParser()
    parser.add_argument('-a')

    subs = parser.add_subparsers(dest='cmd')
    sub = subs.add_parser('sub')
    sub.add_argument('-b')

    ns = parser.parse_args(['-a', '1', 'sub', '-b=2'])

    assert ns.a == '1'
    assert ns.sub.b == '2'
    assert not hasattr(ns, 'b')


def test_cmd(app, loop):
    argv = ['cmd', 'serve', '--listen=0.0.0.0', '--static', 'test']

    with patch('sys.argv', new=argv):
        with app.configure(loop=loop) as config:
            config.include('aiotraversal.cmd')
            config.include('aiotraversal.logger')
            config.include('aiotraversal.serve')

    assert 'cmd' in app
    assert 'args' in app['cmd']
    assert app['cmd']['args'].loglevel == 'WARNING'
    assert 'parser' in app['cmd']
    assert 'subparsers' in app['cmd']
    assert 'parser_serve' in app['cmd']
    assert app['http']['host'] == '0.0.0.0'
    assert app['http']['port'] == 8080


def test_settings(app, loop, settings_ini):
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


def test_run(app, loop):
    argv = ['cmd', 'test']

    run_test = Mock()

    with patch('sys.argv', new=argv):
        with app.configure(loop=loop) as config:
            config.include('aiotraversal.cmd')

            subparsers = config['cmd']['subparsers']
            parser = subparsers.add_parser('test')
            parser.set_defaults(func=run_test)

        assert app['run_func'] == run_test
        run_test.assert_not_called()
        run(app, loop)
        run_test.assert_called_with(app, loop)
