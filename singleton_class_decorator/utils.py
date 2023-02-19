from typing import Callable


def make_ignore_extra_args_wrapper(func: Callable) -> Callable:
    """Wrap the input function into a fuction that can receive more arguments than the input function.

    If the input function is `object.__new__`, all the extra argument will be ignored.

    Args:
        func (Callable): A function that has at least one positional argument

    Returns:
        Callable: A function whose output is the same as the the input function
    """

    def func_wrapper(*args, **kwargs):

        # if the input func is `object.__new__`, ignore all but the first positional argument
        if func is object.__new__:
            return func(args[0])

        return func(*args, **kwargs)

    func_wrapper.__qualname__ = func.__qualname__

    return func_wrapper
