"""The first two sections of grade 10 algebra."""


def get_lessons():
    from .numbers import LESSONS as numbers
    from .roots import LESSONS as roots
    from .powers import LESSONS as powers
    return numbers + roots + powers
