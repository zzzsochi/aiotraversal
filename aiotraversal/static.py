from aiohttp_traversal.ext.static import add_static, prepare_static_view


def includeme(app):
    app.add_method('add_static', add_static)
    prepare_static_view(app)
