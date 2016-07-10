from functools import wraps
from weakref import WeakValueDictionary

method_cache = WeakValueDictionary()


def algebra_impl(cls):
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


def Union(A, B):
    a_type = A().T()
    b_type = B().T()

    if not a_type == b_type:
        raise TypeError('Cannot union {a} and {b}. {a}.T == {a_type} and {b}.T == {b_type} and {a_type} != {b_type}'.format(
                a=A.__name__,
                b=B.__name__,
                a_type=a_type.__name__,
                b_type=b_type.__name__,
            ))

    UnionClass = type(
        A.__name__ + B.__name__,
        (A, B),
        {},
    )
    return UnionClass


