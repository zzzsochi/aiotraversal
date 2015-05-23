import inspect

from zope.dottedname.resolve import resolve


def resolver(*for_resolve):
    """ Resolve dotted names

    Usage:

        @resolver('klass1', 'klass2')
        def method(app, klass1, param, klass2):
            "klass1 and klass2 may be object or dotted notation path"
            assert not isinstance(klass1, str)
            assert not isinstance(klass2, str)
            assert isinstance(param, str)
    """
    def decorator(func):
        spec = inspect.getargspec(func).args[1:]
        if set(for_resolve) - set(spec):
            raise ValueError('bad arguments')

        def wrapper(app, *args, **kwargs):
            module = getattr(app, '_module', None)

            args = list(args)

            for item in for_resolve:
                n = spec.index(item)
                if n >= len(args):
                    continue

                if n is not None and isinstance(args[n], str):
                    args[n] = resolve(args[n], module)

            for kw, value in kwargs.copy().items():
                if kw in for_resolve and isinstance(value, str):
                    kwargs[kw] = resolve(value, module)

            return func(app, *args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__

        return wrapper

    return decorator
