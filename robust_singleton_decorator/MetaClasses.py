from robust_singleton_decorator.cache import Cache
from robust_singleton_decorator.utils import make_ignore_extra_args_wrapper

"""
Three meta-classes that allow to define the possible of child classes' behaviors for the classes defined throught the
sngleton decorator.

"""


class Final(type):
    """Meta-class that can be used in order to prevent the output class to be used as a base class"""

    def __new__(cls, name, bases, classdict):
        for b in bases:
            if isinstance(b, Final):
                raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))
        return type.__new__(cls, name, bases, dict(classdict))


class _SingletonChildren(type):
    """
    Meta-class creatting a class such that, if this class has a `__cache: Cache` attribute,
    every of its children class has the attribute `__cache` set to
    `Cache(is_singleton=True)`
    """

    def __new__(cls, name, bases, classdict):
        for b in bases:
            if hasattr(b, "__cache") and isinstance(b, _SingletonChildren):
                classdict.update({"__cache": Cache(is_singleton=True)})
                break

        return type.__new__(cls, name, bases, classdict)


class _NonSingletonChildren(type):
    """
    Meta-class creatting a class such that, if this class has a `__cache: Cache` attribute,
    every of its children class has the attribute `__cache` set to
    `Cache(is_singleton=False)`
    """

    def __new__(cls, name, bases, classdict):
        for b in bases:
            if hasattr(b, "__cache") and isinstance(b, _NonSingletonChildren):
                classdict.update({"__cache": Cache(is_singleton=False)})
                break

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
