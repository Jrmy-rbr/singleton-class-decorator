from singleton_class_decorator.utils import make_ignore_extra_args_wrapper
from typing import Type
from hashlib import sha256

INSTANCE_NAME = "instance" + sha256("instance".encode()).hexdigest()  # the hash is used for the unicity of the name
OLD_NEW_NAME = "old_new" + sha256("old_new".encode()).hexdigest()  # the hash is used for the unicity of the name
"""
Two meta-classes that allow to define the classes output by the singleton decorator.
"""


# * Define the new function that will be used to overwrite the __new__ function
# * in the classes created by the metaclasses returned by _get_metaclasses


def new(klass: Type, *args, **kwargs):
    # act as getattr(klass, OLD_NEW_NAME) in the
    # case in which the klass redefines its __new__ method,
    # and for which the __new__ method of its *parent* class was *this* new function
    # This is because a singleton's child should not be a singleton itself
    if "__new__" in klass.__dict__ and klass.__new__ is not new and klass.__mro__[1].__new__ is new:
        old_new = make_ignore_extra_args_wrapper(getattr(klass, OLD_NEW_NAME))
        return old_new(klass, *args, **kwargs)

    # Cash the first instance of the class
    if not hasattr(klass, INSTANCE_NAME):
        old_new = make_ignore_extra_args_wrapper(getattr(klass, OLD_NEW_NAME))
        setattr(klass, INSTANCE_NAME, old_new(klass, *args, **kwargs))

    return getattr(klass, INSTANCE_NAME)


# * Define the __new__ functions that'll be used in the Metaclasses defined below


def make_singleton__new__(meta_cls, name, bases, classdict, make_singleton: bool = False):
    old_class = type(meta_cls).__new__(meta_cls, name, bases, classdict)

    # Make the singleton class if make_singleton
    if make_singleton:
        classdict[OLD_NEW_NAME] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
        classdict["__new__"] = new
        return type(meta_cls).__new__(meta_cls, name, bases, classdict)

    # if not make_singleton, simply forward the __new__/old_new class of the old_class to the new one.
    old_new = classdict["__new__"] if "__new__" in classdict else getattr(old_class, OLD_NEW_NAME, old_class.__new__)
    classdict["__new__"] = make_ignore_extra_args_wrapper(old_new)

    return type(meta_cls).__new__(meta_cls, name, bases, classdict)


def make_final_singleton__new__(meta_cls, name, bases, classdict, make_singleton: bool = True):
    for base in bases:
        if isinstance(base, meta_cls):
            raise TypeError(f"type '{base.__name__}' is not an acceptable base type")

    return super(meta_cls, meta_cls).__new__(meta_cls, name, bases, classdict, make_singleton)


# * Defined the _get_metaclasses function


def _get_metaclasses(klass: Type):
    """Takes a `klass` as input, and return the meta-classes that creates singleton classes.
    This is dones in such a way that these meta-classes inherit from `type(klass)` to avoid
    conflict by using the singleton decorator on classes defined through a meta-class

    Returns:
        Tuple[MakeSingleton, MakeFinalSingleton]: Two meta-classes used in the `singleton` function
            in order to create singleton classes.
    """
    MakeSingleton = type("MakeSingleton", (type(klass),), {"__new__": make_singleton__new__})
    MakeFinalSingleton = type("MakeFinalSingleton", (MakeSingleton,), {"__new__": make_final_singleton__new__})

    return MakeSingleton, MakeFinalSingleton


MakeSingleton, MakeFinalSingleton = _get_metaclasses(type)
