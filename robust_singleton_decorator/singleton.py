from operator import xor
from typing import Any, Dict, Optional
import inspect

import logging
import pytest


def singleton(*arg, **kwarg):
    """Transform an input class into a singleton class. Can be used as a decorator

    Args:
        class_ (Class): A class as a positional argument, whose behavior will be modified
        is_final (bool): Keyword argument. If True the class cannot be used as a base class for inheritance.
            WARNING: Setting it to False can lead to unexpected behaviour for the Child class. Default to True.

    Raises:
        TypeError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    allowed_keyword_argument = {"is_final": bool}
    check_singleton_input(arg, kwarg, allowed_keyword_argument)

    is_final = True if "is_final" not in kwarg else kwarg["is_final"]
    if not is_final:
        logging.warning(
            "`is_final` is set to False. This can lead to unexpected behavior for the child class of this class"
        )

    class Final(type):
        """Meta-class that can be used in order to prevent the output class to be used as a base class"""

        def __new__(cls, name, bases, classdict):
            for b in bases:
                if isinstance(b, Final):
                    raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))
            return type.__new__(cls, name, bases, dict(classdict))

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
            if cls.__already_created and (cls.__cached_args != args or cls.__cached_kwargs != kwargs):
                raise ValueError(
                    f"""This object has already been created, you cannot redefine it with different arguments
                    The initial arguments where:
                    - positional args: {cls.__cached_args},
                    - key wors args: {cls.__cached_kwargs}"""
                )
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
                "__new__": new,
                "__init__": init,
            },
        )

        return NewClass

    if len(arg) == 1:
        return wrapper(arg[0])

    return wrapper


def check_singleton_input(arg, kwarg, allowed_kwarg: Optional[Dict[str, Any]] = None):
    if allowed_kwarg is None:
        allowed_kwarg = dict()

    input_condition_1 = len(arg) == 1 and inspect.isclass(arg[0])
    input_condition_2 = kwarg.keys() == allowed_kwarg.keys()

    if not xor(input_condition_1, input_condition_2):
        raise TypeError(
            f"singleton() either accepts 1 positional class argument or {len(allowed_kwarg)} keyword argument. "
            f"Got {len(arg)} positional argument and {len(kwarg)} keyword argument"
        )

    for arg_name, arg_val in kwarg.items():
        if not isinstance(arg_val, allowed_kwarg[arg_name]):
            raise TypeError(
                f"Keyword argument {arg_name} is expected to be an instance of {allowed_kwarg[arg_name]}. "
                f"Got {type(arg_val)} instead"
            )


