import pytest

from robust_singleton_decorator.MetaClasses import (
    Final,
    _NonSingletonChildren,
    _SingletonChildren,
    SingletonWithSingletonChildren,
    SingletonWithNonSingletonChildren,
    SingletonFinal,
)
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


def test__singleton_children():
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


def test__non_singleton_children():
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


def test_singleton_final_basic():
    class A(metaclass=SingletonFinal):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    a = A(1, 2)
    a2 = A(1, 2)
    assert (a.x, a.y) == (1, 2)
    assert a2 is a

    # Should raise an error when trying to make a children class
    with pytest.raises(TypeError):

        class B(A):
            ...


def test_singleton_children_basic():
    class A(metaclass=SingletonWithSingletonChildren):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    a = A(1, 2)
    a2 = A(1, 2)
    assert (a.x, a.y) == (1, 2)
    assert a2 is a

    class B(A):
        ...

    b = B(2, 3)
    b2 = B(2, 3)
    assert b.x, b.y == (2, 3)
    assert b is b2

    assert a is not b


def test_singleton_with_singleton_children():

    # Try to get a weird definition where one attribut is defined in __new__ and the others in __init__
    class A(metaclass=SingletonWithSingletonChildren):
        def __new__(cls, x, y, z):
            obj = super().__new__(cls)
            obj.z = z
            return obj

        def __init__(self, x, y, z):
            self.x = x
            self.y = y

    a = A(1, 2, 3)
    assert (a.x, a.y, a.z) == (1, 2, 3)

    # check that A instances are the same
    a2 = A(1, 2, 3)
    assert a2 is a

    class B(A):
        def __new__(cls, x, y, z):
            # return the super().__new__ with x, y, z = 0, 0, 0 as input
            # Use the __init__ to overwrite the x, y, z attributes of the object
            return super(B, cls).__new__(cls, 0, 0, 0)

        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    b = B(2, 3, 4)
    assert (b.x, b.y, b.z) == (2, 3, 4)

    # check that B is still a singleton class
    b2 = B(2, 3, 4)
    assert b2 is b

    class C(B):
        ...

    # check that C is still a singleton, but different from A
    c = C(1, 2, 3)
    c2 = C(1, 2, 3)
    assert a is not c
    assert c is c2


def test_singleton_with_non_singleton_children_basic():
    class A(metaclass=SingletonWithNonSingletonChildren):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    # Check that A is a singleton
    a = A(1, 2)
    a2 = A(1, 2)
    assert (a.x, a.y) == (1, 2)
    assert a2 is a

    class B(A):
        ...

    # check that b is not a
    b = B(1, 2)
    assert b.x, b.y == (1, 2)
    assert a is not b

    # check that a second instance of B is not b
    b2 = B(2, 3)
    assert b2.x, b2.y == (2, 3)
    assert b2 is not b


def test_singleton_with_non_singleton_children():
    class A(metaclass=SingletonWithNonSingletonChildren):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class B(A):
        ...

    class C(B):
        ...

    # check that C is not a singleton class
    c = C(1, 2)
    c2 = C(1, 2)
    assert c is not c2
