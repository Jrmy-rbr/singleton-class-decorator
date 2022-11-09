from robust_singleton_decorator.utils import make_ignore_extra_args_wrapper
from robust_singleton_decorator.logging import log

"""
Three meta-classes that allow to define the possible of child classes' behaviors for the classes defined throught the
sngleton decorator.

"""


# * Define the new function that will be used to overwrite the __new__ function
# * in the classes created by the metaclasses below
def new(class_, *args, **kwargs):
    if not hasattr(class_, "instance") or class_.instance is None:
        old_new = make_ignore_extra_args_wrapper(class_._old_new)
        class_.instance = old_new(class_, *args, **kwargs)
    else:
        log.warning(
            "The class has already been instanciated. Returning the same instance of the class. "
            "Any new, or different argument passed to the constructor will be ignored."
        )
    return class_.instance


class SingletonFinal(type):
    """Metaclass creating singleton classes that are final, that is, the created classes cannot be parent classes."""

    def __new__(cls, name, bases, classdict):
        for b in bases:
            if isinstance(b, SingletonFinal):
                raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))

        old_class = type.__new__(cls, name, bases, classdict)
        classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
        classdict["__new__"] = new

        return type.__new__(cls, name, bases, dict(classdict))


class SingletonWithSingletonChildren(type):
    """Metaclass creating singleton classes whose children are **also** singleton classes."""

    def __new__(cls, name, bases, classdict):
        old_class = type.__new__(cls, name, bases, classdict)

        if not bases or not any([isinstance(b, SingletonWithSingletonChildren) for b in bases]):
            classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
            classdict["__new__"] = new
        else:
            classdict["instance"] = None

        return type.__new__(cls, name, bases, classdict)


class SingletonWithNonSingletonChildren(type):
    """Metaclass creating singleton classes whose children are **not** singleton classes."""

    def __new__(cls, name, bases, classdict):
        old_class = type.__new__(cls, name, bases, classdict)

        if not bases or not any([isinstance(b, SingletonWithNonSingletonChildren) for b in bases]):
            classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
            classdict["__new__"] = new
        else:
            if "__new__" not in classdict:
                old_new = old_class._old_new
            else:
                log.warning(
                    "You are overwriting the __new__ method of a class that inherits from a singleton class."
                    " This may lead to unexpected behavior"
                )
                old_new = classdict["__new__"]

            classdict["__new__"] = make_ignore_extra_args_wrapper(old_new)

        return type.__new__(cls, name, bases, classdict)


# * Define the new function that will be used to overwrite the __new__ function
# * in the classes created by the metaclasses below
def new(class_, *args, **kwargs):
    if not hasattr(class_, "instance") or class_.instance is None:
        old_new = make_ignore_extra_args_wrapper(getattr(class_, "__old_new"))
        class_.instance = old_new(class_, *args, **kwargs)
    return class_.instance


class SingletonFinal(type):
    """Metaclass creating singleton classes that are final, that is, the created classes cannot be a parent classes."""

    def __new__(cls, name, bases, classdict):
        for b in bases:
            if isinstance(b, SingletonFinal):
                raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))

        old_class = type.__new__(cls, name, bases, classdict)
        classdict["__new__"] = new
        classdict["__old_new"] = old_class.__new__

        return type.__new__(cls, name, bases, dict(classdict))


class SingletonWithSingletonChildren(type):
    """Metaclass creating singleton classes whose children are **also** singleton classes."""

    def __new__(cls, name, bases, classdict):
        old_class = type.__new__(cls, name, bases, classdict)

        if not bases or not any([isinstance(b, SingletonWithSingletonChildren) for b in bases]):
            classdict["__new__"] = new
            classdict["__old_new"] = old_class.__new__
        else:
            classdict["instance"] = None

        return type.__new__(cls, name, bases, classdict)


class SingletonWithNonSingletonChildren(type):
    """Metaclass creating singleton classes whose children are **not** singleton classes."""

    def __new__(cls, name, bases, classdict):
        old_class = type.__new__(cls, name, bases, classdict)

        if not bases or not any([isinstance(b, SingletonWithNonSingletonChildren) for b in bases]):
            classdict["__new__"] = new
            classdict["__old_new"] = old_class.__new__
        else:
            classdict["__new__"] = make_ignore_extra_args_wrapper(getattr(old_class, "__old_new"))

        return type.__new__(cls, name, bases, classdict)
