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


def test_signleton_no_var_in_constructor():
    @singleton
    class TestClass:
        def __init__(self):
            self.val = 3

    obj_1 = TestClass()
    obj_2 = TestClass()

    assert obj_1 is obj_2


def test_inheritance():
    @singleton
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    # Check that inheritance fails
    with pytest.raises(TypeError):

        class TestChildClass(TestBaseClass):
            ...

    # check that inheritance works
    @singleton(is_final=False)
    class TestBaseClass2:
        def __init__(self):
            self.val = 3

    class TestChildClass2(TestBaseClass2):
        ...
