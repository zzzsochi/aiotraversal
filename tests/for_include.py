def includeme(config):
    config['test_include_info'] = ('includeme', config)
    assert config is not config._include_object


def func(config):
    config['test_include_info'] = ('func', config)
    assert config is not config._include_object


not_callable = 'not callable data'
