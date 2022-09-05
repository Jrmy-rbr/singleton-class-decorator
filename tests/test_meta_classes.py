import pytest

from robust_singleton_decorator.MetaClasses import Final, SingletonChildren, NonSingletonChildren
from robust_singleton_decorator.singleton import singleton


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
    @singleton(is_final=False)
    class A(metaclass=SingletonChildren):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    assert isinstance(A, SingletonChildren)

    a = A(1, 2)
    assert a.x == 1 and a.y == 2

    class B(A):
        ...

    # check that B is also a singleton
    b = B(2, 3)

    with pytest.raises(ValueError) as e:
        b2 = B(3, 4)
    assert "This object has already been created, you cannot redefine it with different arguments" in str(e)

    b3 = B(2, 3)
    assert b is b3


def test_non_singleton_children():
    @singleton(is_final=False)
    class A(metaclass=NonSingletonChildren):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    assert isinstance(A, NonSingletonChildren)

    a = A(1, 2)
    assert a.x == 1 and a.y == 2

    a2 = A(1, 2)
    assert a2 is a

    class B(A):
        ...

    b1 = B(1, 2)
    assert b1.x == 1 and b1.y == 2

    b2 = B(1, 3)

    assert b2 is not b1


if __name__ == "__main__":
    test_non_singleton_children()
