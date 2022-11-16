import math
import pytest

from robust_singleton_decorator.singleton import singleton


def test_singleton_var_in_constructor():
    @singleton
    class TestClass:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    obj_1 = TestClass(3, 4)
    assert obj_1.x == 3
    assert obj_1.y == 4

    obj_3 = TestClass(1, 4)  # check that new arguments are ignored
    assert obj_1 is obj_3


@pytest.mark.parametrize("is_final", [(False,), (True,)])
def test_method_usage(
    is_final,
):
    # Create a class with some method to check whther the methods can be used as expected
    @singleton(is_final=is_final)
    class TestClass:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def add(self):
            return self.x + self.y

        def identity(self, x):
            return x

        @classmethod
        def class_identity(cls, x):
            return x

        @staticmethod
        def cos(x):
            return math.cos(x)

    obj = TestClass(1, 2)

    assert obj.add() == 3
    assert obj.identity(4) == 4
    assert TestClass.class_identity(5) == 5
    assert TestClass.cos(3) == math.cos(3)


def test_signleton():
    @singleton
    class TestClass:
        def __init__(self):
            self.val = 3

    obj_1 = TestClass()
    obj_2 = TestClass()

    assert obj_1 is obj_2


def test_default_inheritance():
    @singleton
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    # Check that, by default, inheritance fails
    with pytest.raises(TypeError):

        class TestChildClass(TestBaseClass):
            ...


def test_singleton_children_inheritance():
    # check that inheritance works
    @singleton(is_final=False)
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    # By default, a children of a Singleton is not a singleton
    # one needs to use the singleton decorator to make it a singleton
    class TestChildClass(TestBaseClass):
        ...

    a = TestChildClass()
    a2 = TestChildClass()

    assert a is not a2

    # check one can use the singleton decorator on a child class
    @singleton
    class TestOtherChildClass(TestBaseClass):
        ...

    b = TestOtherChildClass()
    b2 = TestOtherChildClass()

    assert b is b2


def test_non_singleton_children_inheritance():
    # check that inheritance works
    @singleton(is_final=False)
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    # check that TestBaseClass is a singleton
    a = TestBaseClass()
    a2 = TestBaseClass()

    assert a is a2

    # test that TestChildrenClass is not a singleton
    class TestChildClass(TestBaseClass):
        ...

    b = TestChildClass()
    b2 = TestChildClass()

    assert b is not b2


@pytest.mark.parametrize("is_final", [(False,), (True,)])
def test_decorator_with_redefined_new(is_final):
    @singleton(is_final=is_final)
    class TestBaseClass:
        def __new__(cls, val0, val):
            obj = super().__new__(cls)
            obj.val0 = val0

            return obj

        def __init__(self, val0, val):
            self.val = val

    a = TestBaseClass(1, 13)
    assert (a.val0, a.val) == (1, 13)

    a2 = TestBaseClass(1, 2)
    assert a is a2

    if not is_final:

        class TestChildClass(TestBaseClass):
            def __new__(cls, val0, val):
                obj = super().__new__(cls, val0, val)

                obj.val0, obj.val = 2, 3
                return obj

            def __init__(self, val0, val):
                ...

        b = TestChildClass(3, 5)
        assert (b.val0, b.val) == (2, 3)

        b2 = TestChildClass(3, 5)
        assert b is not b2


def test_singleton_non_children_singleton_case_overwrite_new():
    @singleton(is_final=False)
    class TestBaseClass:
        def __new__(cls, val0, val):
            obj = super().__new__(cls)
            obj.val0 = val0

            return obj

        def __init__(self, val0, val):
            self.val = val

    # If one wants to overwrite the __new__ method of a method inheriting from a singletion class, one should
    # use the __new__ method from object internally, not super().__new__
    class TestChildClass(TestBaseClass):
        def __new__(cls, val0, val):
            obj = object.__new__(cls)

            obj.val0, obj.val = 2, 3
            return obj

        def __init__(self, val0, val):
            ...

    b = TestChildClass(3, 5)
    assert (b.val0, b.val) == (2, 3)

    b2 = TestChildClass(3, 5)
    assert b is not b2


def test_singleton_non_children_singleton_case_overwrite_new_2():
    @singleton(is_final=False)
    class TestBaseClass:
        def __new__(cls, val0, val):
            obj = super().__new__(cls)
            obj.val0 = val0

            return obj

        def __init__(self, val0, val):
            self.val = val

    # If one wants to overwrite the __new__ method of a method inheriting from a singletion class, one should
    # not use not super().__new__. Instead they should use one of the following ways:
    # - Internally use the __new__ method from `object`,
    # - Internally use the `_old_new` method from cls
    # - Internally use super()._old_new
    class TestChildClass(TestBaseClass):
        def __new__(cls, val0, val):
            obj = super()._old_new(cls, val0, val)

            obj.val0, obj.val = 2, 3
            return obj

        def __init__(self, val0, val):
            ...

    b = TestChildClass(3, 5)
    assert (b.val0, b.val) == (2, 3)

    b2 = TestChildClass(3, 5)
    assert b is not b2
