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


class SingletonChildren(type):
    """
    Meta-class that allows inheritance, such that the children classes are also singleton by default.
    """

    def __new__(cls, name, bases, classdict):
        attributes = ["__already_created", "__cached_obj", "__cached_args", "__cached_kwargs", "__is_singleton"]
        for b in bases:
            if all([hasattr(b, attr) for attr in attributes]) and isinstance(b, SingletonChildren):
                classdict.update(
                    {
                        "__already_created": False,
                        "__cached_obj": None,
                        "__cached_args": None,
                        "__cached_kwargs": None,
                        "__is_singleton": True,
                    }
                )

        return type.__new__(cls, name, bases, classdict)


class NonSingletonChildren(type):
    """
    Meta-class that allows inheritance, such that the children classes are not singleton by default.
    """

    def __new__(cls, name, bases, classdict):
        attributes = ["__already_created", "__cached_obj", "__cached_args", "__cached_kwargs", "__is_singleton"]
        for b in bases:
            if all([hasattr(b, attr) for attr in attributes]) and isinstance(b, NonSingletonChildren):
                classdict.update(
                    {
                        "__already_created": False,
                        "__cached_obj": None,
                        "__cached_args": None,
                        "__cached_kwargs": None,
                        "__is_singleton": False,
                    }
                )
        return type.__new__(cls, name, bases, classdict)
