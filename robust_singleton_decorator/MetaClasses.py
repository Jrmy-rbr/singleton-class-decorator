from robust_singleton_decorator.utils import make_ignore_extra_args_wrapper
from hashlib import sha256

INSTANCE_NAME = "instance" + sha256("instance".encode()).hexdigest()  # the hash is used for the unicity of th name

"""
Two meta-classes that allow to define the classes output by the singleton decorator.

"""


# * Define the new function that will be used to overwrite the __new__ function
# * in the classes created by the metaclasses below
def new(class_, *args, **kwargs):
    # act as class_._old_new in the
    # case in which the class_ redefines its __new__ method,
    # and for which the __new__ method of its *parent* class was *this* new function
    if "__new__" in class_.__dict__ and class_.__new__ is not new and class_.__mro__[1].__new__ is new:
        old_new = make_ignore_extra_args_wrapper(class_._old_new)
        return old_new(class_, *args, **kwargs)

    # Cash the first instance of the class
    if not hasattr(class_, INSTANCE_NAME):
        old_new = make_ignore_extra_args_wrapper(class_._old_new)
        setattr(class_, INSTANCE_NAME, old_new(class_, *args, **kwargs))

    return getattr(class_, INSTANCE_NAME)


class MakeSingleton(type):
    """Metaclass creating singleton classes whose children are **not** singleton classes."""

    def __new__(cls, name, bases, classdict, make_singleton: bool = False):
        old_class = type(cls).__new__(cls, name, bases, classdict)

        # Make the singleton class if make_singleton
        if make_singleton:
            classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
            classdict["__new__"] = new
            return type(cls).__new__(cls, name, bases, classdict)

        # if not make_singleton, simply forward the __new__/_old_new class of the old_class to the new one.
        old_new = classdict["__new__"] if "__new__" in classdict else getattr(old_class, "_old_new", old_class.__new__)
        classdict["__new__"] = make_ignore_extra_args_wrapper(old_new)

        return type(cls).__new__(cls, name, bases, classdict)


class MakeFinalSingleton(MakeSingleton):
    """Metaclass creating singleton classes that cannot have children"""

    def __new__(cls, name, bases, classdict, make_singleton: bool = True):
        for b in bases:
            if isinstance(b, MakeFinalSingleton):
                raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))

        return super().__new__(cls, name, bases, classdict, make_singleton)
