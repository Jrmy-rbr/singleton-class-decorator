from typing import Callable
from collections import Counter
from inspect import signature


def make_ignore_extra_args_wrapper(func: Callable) -> Callable:
    """Wrap the input function into a fuction that can receive more arguments than the input function.
    If the input function has only 1 argument, all the extra argument will be ignored.

    Args:
        func (Callable): A function that has at least one positional argument

    Returns:
        Callable: A function whose output is the same as the the input function
    """

    def func_wrapper(*args, **kwargs):
        # get the number of argument of `new_func` from the signature
        nb_args = Counter(str(signature(func)))[","] + 1

        # if `nb_args` == 1, or if the input func is `object.__new__`, ignore all but the first positional argument
        if nb_args == 1 or func is object.__new__:
            return func(args[0])

        return func(*args, **kwargs)

    func_wrapper.__qualname__ = func.__qualname__

    return func_wrapper
