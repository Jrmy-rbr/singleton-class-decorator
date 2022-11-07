import logging
from typing import Callable
from robust_singleton_decorator.cache import Cache

from robust_singleton_decorator.MetaClasses import Final, _SingletonChildren, _NonSingletonChildren


def singleton(class_=None, /, *, is_final=True, must_children_be_singleton=False):
    """Transform an input class into a singleton class. Can be used as a decorator

    Args:
        class_ (Class): A class as a positional argument, whose behavior will be modified
        is_final (bool): Keyword argument. If True the class cannot be used as a base class for inheritance.
            WARNING: Setting it to False can lead to unexpected behaviour for the Child class. Default to True.

    Returns:
        _type_: _description_
    """

    if not is_final:
        logging.warning(
            "`is_final` is set to False. This can lead to unexpected behavior for the child class of this class"
        )

    def wrapper(class_):
        """Take a class as input. Creates and returns a subclass
        that acts as a singleton.

        This can be used as a decorator

        Args:
            class_ (Class): The class that we want to modify

        Return
            NewClass: a subclass of the input that acts as a singleton.
        """
        new: Callable = _make_new__new__(class_)
        init: Callable = _make_new__init__(class_)

        # * Dynamically create the new class and overwrite its __new__ and __init__ method
        MetaClass = _get_metaclass(is_final, must_children_be_singleton)
        NewClass = MetaClass(
            class_.__name__, (class_,), {"__cache": Cache(is_singleton=True), "__new__": new, "__init__": init}
        )

        return NewClass

    if class_ is not None:
        return wrapper(class_)

    return wrapper


def _get_metaclass(is_final, must_children_be_singleton):
    if is_final:
        MetaClass = Final
    elif not is_final and must_children_be_singleton:
        MetaClass = _SingletonChildren
    else:
        MetaClass = _NonSingletonChildren

    return MetaClass


def _make_new__new__(class_):
    def new(cls, *args, **kwargs):
        if not cls.__cache.is_singleton:
            return class_.__new__(cls)

        if cls.__cache.obj is None:
            assert cls.__cache.args is None and cls.__cache.kwargs is None
            cls.__cache.args, cls.__cache.kwargs = args, kwargs
            cls.__cache.obj = class_.__new__(cls)
        return cls.__cache.obj

    return new


def _make_new__init__(class_):
    def init(self, *args, **kwargs):
        """
        Replacement of the cls.__init__()

        Raises:
            ValueError: Raise an error when the constructor is called with some arguments, but that the
            object has already been created.
        """
        cls = self.__class__

        if not cls.__cache.is_singleton:
            class_.__init__(self, *args, **kwargs)
            return None  # end the init here

        if cls.__cache.already_created and (cls.__cache.args != args or cls.__cache.kwargs != kwargs):
            logging.warning(
                f"""This object has already been created, with different argument. Since it is a singleton
                    object, you cannot change the arguments. The current argument will be ignored.
                    The initial arguments where:
                    - positional args: {cls.__cache.args},
                    - key wors args: {cls.__cache.kwargs}"""
            )
            args, kwargs = cls.__cache.args, cls.__cache.kwargs
        class_.__init__(self, *args, **kwargs)
        cls.__cache.already_created = True

    return init
