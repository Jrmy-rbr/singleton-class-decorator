import pytest

from robust_singleton_decorator.MetaClasses import Final, _NonSingletonChildren, _SingletonChildren
from robust_singleton_decorator.cache import Cache


def test_final():
    class A(metaclass=Final):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    # quickly checking that the class work as intended
    a = A(1, 2)
    assert a.x == 1 and a.y == 2

    # test that A cannot be use as a base class
    with pytest.raises(TypeError) as e:

        class B(A):
            ...

    assert "type 'A' is not an acceptable base type" in str(e)


def test_singleton_children():
    class A:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    # overwrite A using the  _SingletonChildren metaclass
    A = _SingletonChildren(A.__name__, A.__mro__, {"__cache": Cache(is_singleton=False)})
    assert isinstance(A, _SingletonChildren)

    a = A(1, 2)
    assert a.x == 1 and a.y == 2

    assert a.__cache == Cache(is_singleton=False)

    # check that when inheriting from A, the class B changes its cache attribute
    class B(A):
        ...

    b = B(2, 3)

    assert b.__cache == Cache(is_singleton=True)


def test_non_singleton_children():
    class A:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    # overwrite A using the  _NonSingletonChildren metaclass
    A = _NonSingletonChildren(A.__name__, A.__mro__, {"__cache": Cache(is_singleton=True)})
    assert isinstance(A, _NonSingletonChildren)

    a = A(1, 2)
    assert a.x == 1 and a.y == 2
    assert a.__cache == Cache(is_singleton=True)

    # check that when inheriting from A, the class B changes its cache attribute
    class B(A):
        ...

    b = B(1, 2)
    assert b.x == 1 and b.y == 2
    assert b.__cache == Cache(is_singleton=False)


if __name__ == "__main__":
    test_non_singleton_children()
