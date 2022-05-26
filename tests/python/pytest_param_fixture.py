"""
Errr, pytest fixtures.

pytest ~/misc/tests/python/pytest_param_fixture.py -s -v
"""
import pytest


def param_generator():
    yield 'option1'
    yield 'option2'


@pytest.mark.parametrize('param', param_generator())
def test_something(param):
    print('param = {!r}'.format(param))
    pass
