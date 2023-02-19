from typing import Type, Optional
from singleton_class_decorator.MetaClasses import _get_metaclasses


def singleton(klass: Optional[Type] = None, /, *, is_final: bool = True):
    """Transform an input class into a singleton class. Can be used as a decorator

    Args:
        klass (Optional[Type]): A class as a positional argument, whose behavior will be modified
        is_final (bool): Keyword argument. If True the class cannot be used as a base class for inheritance.

    Returns:
        NewClass: a subclass of the input that acts as a singleton.
    """

    def wrapper(klass: Type):
        """Take a class as input. Creates and returns a subclass
        that acts as a singleton.

        Args:
            klass (Type): The class that we want to modify

        Return
            Type: a subclass of the input that acts as a singleton.
        """
        # Dynamically create the Metaclass, so that MetaClass inherit from type(klass)
        # This is done so that singleton can be used on classes that use another meta-class
        MetaClass = _get_metaclasses(klass)[int(is_final)]
        # Dynamically create the new class using on of the MetaClass
        return MetaClass(klass.__name__, (klass,), dict(), make_singleton=True)

    return wrapper(klass) if klass is not None else wrapper
