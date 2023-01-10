from robust_singleton_decorator.MetaClasses import MakeSingleton, MakeFinalSingleton


def singleton(class_=None, /, *, is_final=True):
    """Transform an input class into a singleton class. Can be used as a decorator

    Args:
        class_ (Class): A class as a positional argument, whose behavior will be modified
        is_final (bool): Keyword argument. If True the class cannot be used as a base class for inheritance.
            WARNING: Setting it to False can lead to unexpected behaviour for the Child class. Default to True.

    Returns:
        NewClass: a subclass of the input that acts as a singleton.
    """

    def wrapper(class_):
        """Take a class as input. Creates and returns a subclass
        that acts as a singleton.

        Args:
            class_ (Class): The class that we want to modify

        Return
            NewClass: a subclass of the input that acts as a singleton.
        """

        # * Dynamically create the new class using on of the meta classes
        MetaClass = MakeFinalSingleton if is_final else MakeSingleton
        return MetaClass(class_.__name__, (class_,), dict(), make_singleton=True)

    return wrapper(class_) if class_ is not None else wrapper
