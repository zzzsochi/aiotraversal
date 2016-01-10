from aiohttp_traversal.ext.static import add_static, prepare_static_view


def includeme(config):
    config.add_method('add_static', add_static)
    prepare_static_view(config)
