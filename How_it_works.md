## A first "naive" approach

If one were to write a singleton class, one of the possible ways of doing is to overwrite the `__new__` function of that class following a classic design pattern as follows:

``` python
class SingletonClass:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def some_methds(self): 
        ...
```

The singleton decorator essentially does this: It overwrites the `__new__` function of its input class. An easy implementation of it would then be,
```python
def singleton(klass):
    # This is the function that will overwirete the `__new__` function of the input `klass`
    def new_overwrite(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(klass, cls).__new__(cls)
        return cls.instance

    klass.__new__ = new_overwrite
    return klass
```

However, with this solution, if the user wants to create a child class `ChildClass` from the initial singleton class, not only the child class will be a singleton class (and the user has no control over this), but worse, the instance of the child class and its parent class will be the same:

```python
# this is the singleton has written above
@singleton
class SingletonClass:
    ...

class ChilClass(SingletonClass):
    ...

# The assert passes
assert SingletonClass() is ChildClass()
```

There are several ways for solving this issue. 
For example, one could simply forbid inheritance for Singleton classes. 
It would work but it is not satisfactory in my opinion, as then singleton classes would behave somewhat differently than ordinary classes. 
Also, I do believe that this simple solution requires the use of meta-classes. 
So if I'm going to use meta-classes I might as well use them for something a bit more sophisticated than forbidding inheritance.

And this is exactly what I have done. I've used a meta-class called `MakeSingleton` that takes care of overwriting the `__new__` method of the input class of my singleton decorator. 

## The MakeSingleton meta-class

Now, If I allow inheritance I need to choose whether children classes of a singleton class should also be a singleton. My choice is to let the user of the singleton decorator decide what they want. I had at least two ways to go with this. One way is that I could have added a boolean key argument in my singleton decorator specifying whether children of singleton classes will also be singletons. I find it inelegant as it forces the user to specify the behavior of the child class in the definition of the parent class, instead of in the definition of the child class itself. Using it would look like the following:
```python
# definition of the Parent with the singleton
@singleton(children_are_singleton=True)
class ParentSingleton:
    ...


# definition of the Child class
class ChildClass(ParentClass):
    # In this example, this will be a singleton, but we can't see it only by looking at the definition of the child class
    ...
```

Therefore I chose another option, which is that by default, children classes of singleton classes do not themselves behave as a singleton unless one uses the singleton decorator on them:
```python
# definition of the Parent with the singleton
@singleton
class ParentSingleton:
    ...

class ChildClass_1(ParentClass):
    # Not a sngleton class
    ...

@singleton
class ChildClass_2(ParentClass):
    # Is a singleton class
    ...
```

Now note that in the actual implementation, I do disable inheritance by default, and one needs to explicitly specify that a singleton class can inherit. Therefore the correct syntax for the above example is,
```python
# definition of the Parent with the singleton decorator, and enabling inheritance by setting `is_final=False`
@singleton(is_finale=False) 
class ParentSingleton:
    ...

class ChildClass_1(ParentClass):
    # Not a sngleton class
    ...

@singleton # here I don't set `is_final` so by default this class cannot be used for inheritance
class ChildClass_2(ParentClass):
    # Is a singleton class
    ...
```

I have chosen to forbid inheritance by default as I believe it's a bit safer if, for example, 
there is an edge case I did not consider in my implementation that causes a bug in child classes. Forbidding inheritance by default prevents the user from mistakenly using a singleton class as a parent class. The user has to make a conscious choice to do so.



The `MakeSingleton` class looks like the following

```python
# This is a slightly simplified version of the actual`MakeSingleton` meta-class.
# Note that the extra `make_singleton` argument is used to manage the default "singletoness" of child classes
class MakeSingleton(type):
    def __new__(cls, name, bases, classdict, make_singleton:bool=False):
        old_class = type.__new__(cls, name, bases, classdict)

        # Make the singleton class if make_singleton
        if make_singleton:
            classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
            classdict["__new__"] = new
            return type.__new__(cls, name, bases, classdict)

        # if not make_singleton, simply forward the __new__/_old_new class of the old_class to the new one.
        old_new = classdict["__new__"] if "__new__" in classdict else getattr(old_class, "_old_new", old_class.__new__)
        classdict["__new__"] = old_new

        return type.__new__(cls, name, bases, classdict)
```

With this kind of meta-class, one can now create singleton classes as follows,

```python
# don't forget the `make_singleton` argument, or else the class will not be a Singleton
MySingletonClass = MakeSingleton("MySingletonClass", (,), dict(), make_singleton=True)
```

With this `MakeSingleton` meta-class, one can already write a singleton decorator that creates singleton classes whose child classes are not singleton by default. This decorator would be:

```python
def singleton(klass):
    # we create a singletion class, passing `klass` as a parent class
    return MakeSingleton(klass.__name__, (klass,), dict(), make_singleton=True)
```

## Disabling inheritance

To disable inheritance I use another meta-class called `MakeFinalSingleton` that inherits from `MakeSingleton` but to which I add a piece of code that disables inheritance:

```python
class MakeFinalSingleton(MakeSingleton):
    def __new__(cls, name, bases, classdict, make_singleton: bool = True):
        # small piece of code that disable inheritance
        for b in bases:
            if isinstance(b, cls):
                raise TypeError(f"type '{b.__name__}' is not an acceptable base type")

        # return the same as its parent class `MakeSingleton`
        return super(cls, cls).__new__(cls, name, bases, classdict, make_singleton)
```

## Putting everything together

Now that we have the `MakeSingleton`, and `MakeFinalSingleton` meta classes, we can add an argument to the singleton decorator so that the user can choose to allow inheritance for their class or not.

```python
# A slightly simplified version of the actual singleton decorator
def singleton(klass= None, /, *, is_final = True):

    def wrapper(klass):
        # Choose which meta class to use
        MetaClass = MakeFinalSingleton if is_final else MakeSingleton

        # Create and return the new singleton class using MetaClass
        return MetaClass(klass.__name__, (klass,), dict(), make_singleton=True)

    return wrapper(klass) if klass is not None else wrapper
```

Note that the internal `wrapper` function is here as a trick to go around the constraint that normally decorators can only take one argument: the input class/function. You may 
see this as a sort of [Currying](https://en.wikipedia.org/wiki/Currying) of the decorator.

## One last caveat

The above implementation of the singleton decorator would work for many classes. But there are some classes for which using it would cause an error. These classes are classes that use another meta-class for their creation. Examples of such classes are pydantic classes. To remedy this, I create the meta-classes `MakeSingleton` and `MakeFinalSingleton` as child classes of the meta-class initially used to create the input `klass` to the singleton decorator. 

To do this I define the `__new__` functions of the `MakeSingleton` and `MakeFinalSingleton` separately as functions. I then create `MakeSingleton` and `MakeFinalSinglton` as classes that use these `__new__` functions, and that use `type(klass)` as their parent class, where `klass` is the input class to the singleton decorator. Note that `type(klass)` will return the meta-class used to create `klass`.

```python
# this is the function that will be used as a `__new__` method for `MakeSingleton`
def make_singleton__new__(meta_cls, name, bases, classdict, make_singleton: bool = False):
    old_class = type(meta_cls).__new__(meta_cls, name, bases, classdict)

    # Make the singleton class if make_singleton
    if make_singleton:
        classdict["_old_new"] = old_class.__new__ if "__new__" not in classdict else classdict["__new__"]
        classdict["__new__"] = new
        return type(meta_cls).__new__(meta_cls, name, bases, classdict)

    # if not make_singleton, simply forward the __new__/_old_new class of the old_class to the new one.
    old_new = classdict["__new__"] if "__new__" in classdict else getattr(old_class, "_old_new", old_class.__new__)
    classdict["__new__"] = old_new

    return type(meta_cls).__new__(meta_cls, name, bases, classdict)

# This is the function that will be used as the __new__ method for the `MakeFinalSingleton`
def make_final_singleton__new__(meta_cls, name, bases, classdict, make_singleton: bool = True):
    for b in bases:
        if isinstance(b, meta_cls):
            raise TypeError("type '{0}' is not an acceptable base type".format(b.__name__))

    return super(meta_cls, meta_cls).__new__(meta_cls, name, bases, classdict, make_singleton)


# Create `MakeSingleton` and `MakeFinalSingleton` using the above __new__ functions and usign `type(klass)` as a base class.
def _get_metaclasses(klass: Type):
    MakeSingleton = type("MakeSingleton", (type(klass),), {"__new__": make_singleton__new__})
    MakeFinalSingleton = type("MakeFinalSingleton", (MakeSingleton,), {"__new__": make_final_singleton__new__})

    return MakeSingleton, MakeFinalSingleton
```

We can then write the singleton decorator as,

```python
def singleton(klass None, /, *, is_final = True):

    def wrapper(klass):
        
        # Dynamically create the Metaclass, so that MetaClass inherit from type(klass)
        MetaClass = _get_metaclasses(klass)[int(is_final)]

        # Create and return the singleton class using on of the MetaClass
        return MetaClass(klass.__name__, (klass,), dict(), make_singleton=True)

    return wrapper(klass) if klass is not None else wrapper
```


That's it. There are still a few edge cases, but this is more than 90% of the implementation.