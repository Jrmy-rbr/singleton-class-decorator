from robust_singleton_decorator.cache import Cache

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
