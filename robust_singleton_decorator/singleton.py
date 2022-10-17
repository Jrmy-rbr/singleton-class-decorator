import logging
from dataclasses import dataclass
from typing import Any, Optional

from robust_singleton_decorator.MetaClasses import Final


def singleton(class_=None, /, *, is_final=True):
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

        def new(cls, *args, **kwargs):
            if not cls.__is_singleton:
                return class_.__new__(cls)

            if cls.__cached_obj is None:
                assert cls.__cached_args is None and cls.__cached_kwargs is None
                cls.__cached_args, cls.__cached_kwargs = args, kwargs
                cls.__cached_obj = class_.__new__(cls)
            return cls.__cached_obj

        def init(self, *args, **kwargs):
            """
            Replacement of the cls.__init__()

            Raises:
                ValueError: Raise an error when the constructor is called with some arguments, but that the
                object has already been created.
            """
            cls = self.__class__

            if not cls.__is_singleton:
                class_.__init__(self, *args, **kwargs)
                return None  # end the init here

            if cls.__already_created and (cls.__cached_args != args or cls.__cached_kwargs != kwargs):
                logging.warning(
                    f"""This object has already been created, with different argument. Since it is a singleton
                    object, you cannot change the arguments. The current argument will be ignored.
                    The initial arguments where:
                    - positional args: {cls.__cached_args},
                    - key wors args: {cls.__cached_kwargs}"""
                )
                args, kwargs = cls.__cached_args, cls.__cached_kwargs
            class_.__init__(self, *args, **kwargs)
            cls.__already_created = True

        # * Dynamically create the new class and overwrite its __new__ and __init__ method
        MetaClass = Final if is_final else type
        NewClass = MetaClass(
            class_.__name__,
            (class_,),
            {
                "__already_created": False,
                "__cached_obj": None,
                "__cached_args": None,
                "__cached_kwargs": None,
                "__is_singleton": True,
                "__new__": new,
                "__init__": init,
            },
        )

        return NewClass

    if class_ is not None:
        return wrapper(class_)

    return wrapper


@dataclass
class Cache:
    is_singleton: bool
    already_created: bool = False
    obj: Optional[Any] = None
    args: Optional[Any] = None
    kwargs: Optional[Any] = None
