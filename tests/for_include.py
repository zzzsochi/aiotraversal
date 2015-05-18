def includeme(app):
    app['test_include_info'] = ('includeme', app)
    assert app is not app._app
    assert app.start == app._app.start


def func(app):
    app['test_include_info'] = ('func', app)
    assert app is not app._app
    assert app.start == app._app.start


not_callable = 'not callable data'
