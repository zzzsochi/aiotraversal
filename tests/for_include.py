def includeme(app):
    app['test_include_info'] = ('includeme', app)
    assert app is not app._include_object
    assert app.start.__func__ == app._include_object.start.__func__


def func(app):
    app['test_include_info'] = ('func', app)
    assert app is not app._include_object
    assert app.start.__func__ == app._include_object.start.__func__


not_callable = 'not callable data'
