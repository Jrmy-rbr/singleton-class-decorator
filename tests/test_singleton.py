import math
import pytest

from singleton_class_decorator.singleton import singleton


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


@pytest.mark.parametrize("is_final", [False, True])
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

    assert TestClass() is TestClass()


def test_default_inheritance():
    @singleton
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    # Check that, by default, inheritance fails
    with pytest.raises(TypeError):

        class TestChildClass(TestBaseClass):
            ...


def test_singleton_inheritance():
    # check that inheritance works
    @singleton(is_final=False)
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    # By default, a children of a Singleton is not a singleton
    # one would need to use the singleton decorator to make it a singleton
    class TestChildClass(TestBaseClass):
        ...

    assert TestChildClass() is not TestChildClass()

    # check one can use the singleton decorator on a child class
    @singleton
    class TestOtherChildClass(TestBaseClass):
        ...

    assert TestOtherChildClass() is TestOtherChildClass()


def test_decorator_with_redefined_new():
    @singleton
    class TestBaseClass:
        def __new__(cls, val0, val):
            obj = object.__new__(cls)
            obj.val0 = val0

            return obj

        def __init__(self, val0, val):
            self.val = val

    obj_1 = TestBaseClass(1, 13)
    assert (obj_1.val0, obj_1.val) == (1, 13)

    assert obj_1 is TestBaseClass(1, 2)  # the arguments here should be ignored


def test_decorator_with_redefined_new_and_inheritence():
    @singleton(is_final=False)
    class TestBaseClass:
        def __new__(cls, val0, val):
            obj = object.__new__(cls)
            obj.val0 = val0

            return obj

        def __init__(self, val0, val):
            self.val = val

    class TestChildClass(TestBaseClass):
        def __new__(cls, val0, val):
            obj = super().__new__(cls, val0, val)

            obj.val0, obj.val = 2, 3
            return obj

        def __init__(self, val0, val):
            ...

    obj = TestChildClass(3, 5)
    assert (obj.val0, obj.val) == (2, 3)
    assert obj is not TestChildClass(3, 5)


def decorator_with_redefined_new_and_inheritence_2():
    @singleton(is_final=False)
    class TestBaseClass:
        def __new__(cls, val0, val):
            obj = super().__new__(cls)
            obj.val0 = val0

            return obj

        def __init__(self, val0, val):
            self.val = val

    class TestChildClass(TestBaseClass):
        def __new__(cls, val0, val):
            obj = super().__new__(cls, val0, val)

            obj.val0, obj.val = 2, 3
            return obj

        def __init__(self, val0, val):
            ...

    obj = TestChildClass(3, 5)
    assert (obj.val0, obj.val) == (2, 3)

    assert obj is not TestChildClass(3, 5)


@pytest.mark.parametrize("is_final", [True, False])
def test_singleton_on_classes_internally_using_a_metaclass(is_final):
    class AMetaClass(type):
        ...

    class BaseClass(metaclass=AMetaClass):
        ...

    @singleton
    class MyClass(BaseClass):
        ...

    # check that BaseClass and therefore MyClass internally already use a meta-class
    assert type(BaseClass) != type

    # Check that MyClass is still an instance of AMetaClass
    assert isinstance(MyClass, AMetaClass)

    # check that MyPydanticClass is a singleton
    assert MyClass() is MyClass()
