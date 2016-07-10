from functools import wraps
from weakref import WeakValueDictionary


def algebra_impl(cls):
    method_cache = WeakValueDictionary()

    def find_abstract_method(cls):
        key = id(cls)
        if key not in method_cache:
            for name in dir(cls):
                member = getattr(cls, name)
                if getattr(member, '__isabstractmethod__', False):
                    method_cache[key] = member
                    return member
            raise TypeError(cls)

        return method_cache[key]

    def decorator(wrapped):
        @wraps(wrapped)
        def wrapper(algebra, *args, **kwargs):
            iface = algebra.T()
            method = find_abstract_method(iface)

            def impl(self):
                return wrapped(algebra, self)

            witness = type(
                iface.__name__ + cls.__name__,
                (cls, iface),
                {method.__name__: impl},
            )

            return witness(*args, **kwargs)

        return wrapper
    return decorator
