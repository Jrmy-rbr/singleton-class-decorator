import pytest

from singleton_class_decorator.MetaClasses import MakeFinalSingleton, MakeSingleton


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

    # test that we can make a SingletonFinal inheriting from a Singleton class

    class D(C, metaclass=MakeFinalSingleton):
        ...

    assert isinstance(D, MakeFinalSingleton)

    d = D(1, 2)
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

    # Should raise an error when trying to make a children class
    with pytest.raises(TypeError):

        class C(B):
            ...


def test_redefining_new():
    A = MakeSingleton("A", (), {}, make_singleton=True)

    # check A is indeed a singleton
    assert A() is A()

    # redefine __new__ using super().__new__internally
    class B(A):
        def __new__(cls):
            return super().__new__(cls)

    # check B() is not a singleton
    assert B() is not B()
