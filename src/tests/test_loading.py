from timeit import timeit
from unittest import TestCase

from ..ipaparser import IPA, load

FACTOR = 10.0


def is_much_larger(a: float, b: float) -> bool:
    return a > b * FACTOR


def are_roughly_equal(a: float, b: float) -> bool:
    return not is_much_larger(a, b) and not is_much_larger(b, a)


class TestLoading(TestCase):
    def test_loading_time(self) -> None:
        loading_time = timeit(load, number=1)
        first_parse = timeit(lambda: IPA('/abc/'), number=1)
        second_parse = timeit(lambda: IPA('/def/'), number=1)
        self.assertTrue(is_much_larger(loading_time, first_parse))
        self.assertTrue(are_roughly_equal(first_parse, second_parse))
