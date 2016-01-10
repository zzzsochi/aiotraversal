from unittest.mock import patch


def test_cmd(loop, app):
    argv = ['cmd', 'serve', '--static', 'test']

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
