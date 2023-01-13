![coverage badge](https://img.shields.io/badge/coverage-100%-brightgreen.svg)
<img title="a title" alt="coverage badge" src="https://img.shields.io/badge/coverage-100%-brightgreen.svg">
              
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
Here are some usage examples:

## Simplest use case

## Enabling Inheritance
