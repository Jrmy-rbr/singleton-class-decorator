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
    @singleton(is_final=False, must_children_be_singleton=True)
    class TestBaseClass:
        def __init__(self):
            self.val = 3

    class TestChildClass(TestBaseClass):
        ...

    a = TestChildClass()
    a2 = TestChildClass()

    assert a is a2


def test_non_singleton_children_inheritance():
    # check that inheritance works
    @singleton(is_final=False, must_children_be_singleton=False)
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
