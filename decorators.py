"""Just some helper decorators."""

from collections.abc import Iterable


def parse_np_float(fn):
    """Parses numpy float64 object to Python native Decimal.decimal object."""

    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        if isinstance(res, Iterable):
            return [
                (float(i[0]), float(i[1])) for i in res
            ]

        return float(res)

    return inner
