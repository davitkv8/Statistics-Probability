"""Just some helper decorators."""

from collections.abc import Iterable


def parse_np_float(fn):
    """Parses numpy float64 object to Python native float object."""

    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        if isinstance(res, Iterable):
            return [
                (float(round(i[0], 1)), float(round(i[1], 1))) for i in res
            ]

        return float(round(res, 1))

    return inner
