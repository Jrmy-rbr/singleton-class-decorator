from robust_singleton_decorator.utils import make_ignore_extra_args_wrapper
from robust_singleton_decorator.logging import log

"""
Two meta-classes that allow to define the classes output by the singleton decorator.

"""


# * Define the new function that will be used to overwrite the __new__ function
# * in the classes created by the metaclasses below
def new(class_, *args, **kwargs):
    if not hasattr(class_, "instance"):
        old_new = make_ignore_extra_args_wrapper(class_._old_new)
        class_.instance = old_new(class_, *args, **kwargs)

    return class_.instance


class MakeSingleton(type):
    """Metaclass creating singleton classes whose children are **not** singleton classes."""

    def __new__(cls, name, bases, classdict, make_singleton: bool = False):
        old_class = type.__new__(cls, name, bases, classdict)

        # Make the singleton class if make_singleton
        if make_singleton:
            classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
            classdict["__new__"] = new
            return type.__new__(cls, name, bases, classdict)

        # if not make_singleton, simply forward the __new__/_old_new class of the old_class to the new one.
        if "__new__" in classdict:
            log.warning(
                "You are overwriting the __new__ method of a class that inherits from a singleton class."
                " This may lead to unexpected behavior"
            )
            old_new = classdict["__new__"]
        else:
            old_new = getattr(old_class, "_old_new", old_class.__new__)

        classdict["__new__"] = make_ignore_extra_args_wrapper(old_new)

        return type.__new__(cls, name, bases, classdict)


class MakeFinalSingleton(MakeSingleton):
    """Metaclass creating singleton classes that cannot have children"""

    def __new__(cls, name, bases, classdict, make_singleton: bool = True):
        for b in bases:
            if isinstance(b, MakeFinalSingleton):
                raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))

        return super().__new__(cls, name, bases, classdict, make_singleton)
