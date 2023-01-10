import pytest

from robust_singleton_decorator.MetaClasses import (
    SingletonWithSingletonChildren,
    SingletonWithNonSingletonChildren,
    SingletonFinal,
    MakeSingleton,
    MakeFinalSingleton,
)


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


def test_make_singleton_class():
    def init_redef(self, x, y):
        self.x = x
        self.y = y

    A = MakeSingleton("A", (), {"__init__": init_redef}, make_singleton=True)

    # check that A is a singleton. Should be the case since we've set make_singleton=True above
    a = A(1, 2)
    a2 = A(2, 3)
    assert a is a2

    # check that a class inheriting from A is not a singleton
    class B(A):
        ...

    b = B(1, 2)
    b2 = B(2, 3)
    assert b is not b2

    # check that we can make a singleton inheriting from B
    C = MakeSingleton("C", (B,), {}, make_singleton=True)

    c = C(2, 3)
    c2 = C(3, 4)
    assert c is c2

    # test that we can make a SingletonFinal inheriting from a Singleton

    class D(C, metaclass=MakeFinalSingleton):
        ...

    d = D(1, 2)
    assert isinstance(D, MakeFinalSingleton)
    d2 = D(3, 4)
    assert d is d2  # check that D is a singleton


def test_make_singleton_final():
    def init_redef(self, x, y):
        self.x = x
        self.y = y

    # check that we can make a singleton inheriting from B
    A = MakeSingleton("A", (), {"__init__": init_redef}, make_singleton=True)

    a = A(2, 3)
    a2 = A(3, 4)
    assert a is a2

    # test that we can make a SingletonFinal inheriting from a Singleton

    class B(A, metaclass=MakeFinalSingleton):
        ...

    assert isinstance(B, MakeFinalSingleton)

    b = B(1, 2)
    b2 = B(3, 4)
    assert b is b2  # check that D is a singleton

    # check we cannot inherit from B
    with pytest.raises(TypeError):

        class C(B):
            ...
