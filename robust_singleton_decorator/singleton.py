import logging
from robust_singleton_decorator.MetaClasses import (
    SingletonFinal,
    SingletonWithNonSingletonChildren,
    SingletonWithSingletonChildren,
)

MUST_CHILDREN_BE_SINGLETON_DEFAULT = False


def singleton(class_=None, /, *, is_final=True, must_children_be_singleton=MUST_CHILDREN_BE_SINGLETON_DEFAULT):
    """Transform an input class into a singleton class. Can be used as a decorator

    Args:
        class_ (Class): A class as a positional argument, whose behavior will be modified
        is_final (bool): Keyword argument. If True the class cannot be used as a base class for inheritance.
            WARNING: Setting it to False can lead to unexpected behaviour for the Child class. Default to True.
        must_children_be_singleton (bool, optional): Keyword argument. Whether the children class of the current
            singleton class must also be singleton.

    Returns:
        NewClass: a subclass of the input that acts as a singleton.
    """

    if is_final and must_children_be_singleton is not MUST_CHILDREN_BE_SINGLETON_DEFAULT:
        logging.warning("`is_final` is set to True, so the `must_children_be_singleton` argument is ignored")

    def wrapper(class_):
        """Take a class as input. Creates and returns a subclass
        that acts as a singleton.

        Args:
            class_ (Class): The class that we want to modify

        Return
            NewClass: a subclass of the input that acts as a singleton.
        """
        # * Check that class_ is not already created fom on the of the Singleton metaclass
        _check_metaclass(class_)

        # * Dynamically create the new class using on of the meta classes
        MetaClass = _get_metaclass(is_final, must_children_be_singleton)
        return MetaClass(class_.__name__, (class_,), dict())

    return wrapper(class_) if class_ is not None else wrapper


def _get_metaclass(is_final, must_children_be_singleton):
    if is_final:
        MetaClass = SingletonFinal
    elif not is_final and must_children_be_singleton:
        MetaClass = SingletonWithSingletonChildren
    else:
        MetaClass = SingletonWithNonSingletonChildren

    return MetaClass


def _check_metaclass(class_) -> None:
    for metaclass in [SingletonFinal, SingletonWithSingletonChildren, SingletonWithNonSingletonChildren]:
        if isinstance(class_, metaclass):
            raise TypeError(
                f"The class {class_.__name__} is an instance of {metaclass.__name__}. "
                f"You cannot use the singleton decorator on classes that derive from instances of {metaclass}. "
                "Please use the singleton decorator on the base class, and use the arguments `is_final` "
                "and ` must_children_be_singleton` to define the behavior of its children classes."
            )
