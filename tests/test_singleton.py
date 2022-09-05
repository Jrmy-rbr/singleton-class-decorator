import pytest
from robust_singleton_decorator.singleton import singleton


def test_singleton_var_in_constructor():
    @singleton
    class TestClass:
        def __init__(self, val1, val2):
            self.val1 = val1
            self.val2 = val2

    obj_1 = TestClass(3, 4)
    assert obj_1.val1 == 3
    assert obj_1.val2 == 4

    with pytest.raises(ValueError) as e:
        obj_2 = TestClass(2, 3)
    assert "This object has already been created, you cannot redefine it with different arguments" in str(e)

    obj_3 = TestClass(3, 4)
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

    with pytest.raises(TypeError) as e:

        class TestChildClass(TestBaseClass):
            ...

    assert "is not an acceptable base type" in str(e)

    @singleton(is_final=False)
    class TestBaseClass2:
        def __init__(self):
            self.val = 3

    class TestChildClass2(TestBaseClass2):
        ...
