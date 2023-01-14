![smth](https://img.shields.io/badge/coverage-100%25-brightgreen)

# Singleton Class Decorator

This repo implements a decorator that creates singleton classes. As opposed to some other singleton decorators,
the singleton classes created through this decorator are true classes. As a consequence,
every operation supported by classes is supported by the singleton classes, like the use of `isinstance`,
or inheritance for example.

The main purpose of this repo was for me to learn more about python, and some of its more advance features. But this decorator comes with its own advantages. It is not really more powerful than for example [this](https://github.com/Kemaweyan/singleton_decorator) commonly used decorator by [Kemaweyan](https://github.com/Kemaweyan). However it allows to uses singleton classes as actual classes, and therefore it might be more intuitive to use in situations where Kemayan's singleton object need to use some extra attribute. Here is a quick illustration of situations in which our decorator behaves differently.

### Kemayan decorator
```python
@singleton
class MyClass:
    @static
    def add(x, y):
        return x+y

# This will rase an AttributeError
MyClass.add(1, 2)

# You need to do this instead. It'll return 3
MyClass.__wrapped__.add(1, 2)
```

```python
@singleton
class MyClass:
    ...

obj = MyClass()

# this will raise an error
isinstance(obj, MyClass)

# you need to do this instead
isinstance(obj, MyClass.__wrapped__)
```

### This decorator

```python
@singleton
class MyClass:
    @static
    def add(x, y):
        return x+y

# This works fine
MyClass.add(1, 2)
```

```python
@singleton
class MyClass:
    ...

obj = MyClass()

# this works fine
isinstance(obj, MyClass)
```

# Usage


## Simplest use case
Here are some usage examples. To make a singleton class you simply need to use the singleton decorator
on your class as follows:

```python
@singleton
class MyClass:
    ...

# MyClass is now a singleton, which we can check
assert MyClass() is MyClass()

```

As mentioned earlier, you can check the type of an object as with a regular class:

```python
obj = MyClass()

type(obj)
# returns `<class 'singleton_class_decorator.MetaClasses.MyClass'>`

type(obj) == MyClass
# This evaluates to True

isinstance(obj, MyClass)
# This evaluates to True

```

## Enabling Inheritance

The above should work for any class. However if you try to create a child class from `MyClass` an error will be raised. This is because by default singleton 
disable inheritance. 
```python
@singleton
class MyClass:
    ...

# is equivalent to the following

@singleton(is_final=True)
class MyClass:
    ...
```
As you see, the default value of the key word argument `is_final` is `True`, which disables inheritance. But you can easily changed.

```python
# enable inheritance by setting the ketword argument `is_final` for `False`
@singleton(is_final=False)
class MyClass:
    ...

# This will now work
class ChildClass(MyClass):
    ...

# However the ClidClass is not automatically a singleton
assert ChildClass() is not ChildClass()

# If you want a child class to be a singleton, you need to use the singleton decorator
# Again you may set the `is_final` to `True` or `False` as you whish.
@singleton
class OtherChildClass(MyClass):
    ...

# OtherChildClass is a singleton
assert OtherChildClass() is OtherChildClass()

```