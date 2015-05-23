from unittest.mock import Mock

import pytest

from aiotraversal.helpers import resolver


def test_resolver():
    class Obj:
        @resolver('obj1', 'obj2')
        def meth(self, obj1, ar, obj2=2, kw=3):
            return (self, obj1, ar, obj2, kw)

    obj = Obj()
    res = obj.meth('os.path.isdir', 'str', obj2='sys.exit')

    from os.path import isdir
    from sys import exit

    assert res[0] is obj
    assert res[1] is isdir
    assert res[2] == 'str'
    assert res[3] is exit
    assert res[4] == 3

    res = obj.meth(isdir, 'str', obj2=exit)

    assert res[0] is obj
    assert res[1] is isdir
    assert res[2] == 'str'
    assert res[3] is exit
    assert res[4] == 3


def test_resolver__relative():
    @resolver('obj')
    def func(app, obj):
        return (app, obj)

    res = func(Mock(name='app', _module='tests'), '.for_include.func')

    from .for_include import func as func_imported
    assert res[0]._module == 'tests'
    assert res[1] is func_imported


def test_resolver__import_error():
    @resolver('obj')
    def func(app, obj):
        return (app, obj)

    with pytest.raises(ImportError):
        func('app', 'not_found')


def test_resolver__declare_error():
    with pytest.raises(ValueError):
        @resolver('not_exist')
        def func(app, obj):
            return (app, obj)
