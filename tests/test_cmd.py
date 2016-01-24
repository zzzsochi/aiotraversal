from unittest.mock import Mock, patch

from aiotraversal.cmd import ArgumentParser, run


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
    assert 'parser' in app['cmd']
    assert 'subparsers' in app['cmd']
    assert 'parser_serve' in app['cmd']
    assert app['loglevel'] == 'WARNING'
    assert app['http']['host'] == '0.0.0.0'
    assert app['http']['port'] == 8080


def test_run(app, loop):
    argv = ['cmd', 'test']

    run_test = Mock()

    with patch('sys.argv', new=argv):
        with app.configure(loop=loop) as config:
            config.include('aiotraversal.cmd')

            subparsers = config['cmd']['subparsers']
            parser = subparsers.add_parser('test')
            parser.set_defaults(func=run_test)

        assert app['cmd']['run_func'] == run_test
        run_test.assert_not_called()
        run(app, loop)
        run_test.assert_called_with(app, loop)
