A quick way to make Python classes automatically memoize (a.k.a. cache) their
instances based on the arguments they are instantiated with (i.e. args to
``__init__``). It's a simple way to avoid repetitively creating
expensive-to-create objects, and to make sure objects that have a
natural 'identity'
are created only once.

Usage
=====

Say you have a class ``Thing`` that requires expensive computation to create, or
that should be created only once. In Python 2.x you can make that happen by
adding one line to its definition::

    from mementos import MementoMetaclass

    class Thing(object):
        
        __metaclass__ = MementoMetaclass  # now I'm memoized!
        
        def __init__(self, name):
            self.name = name
        
        ...

Then ``Thing`` objects will be memoized::

    t1 = Thing("one")
    t2 = Thing("one")
    assert t1 is t2    # same instantiation args => same object
    
Python 3
========

``mementos`` works in Python 3 just as in Python 2, but with different syntax.
Instead of the double-underscore class attribute assignment, Python 3 uses a
keyword argument at class creation::

    class Thing3(object, metaclass=MementoMetaclass):
        ...
       
Unfortunately, Python 2 and Python 3 don't recognize each other's syntax for
metaclass specification, so straightforward code for one won't even compile for
the other. You can get around this by using the ``with_metaclass()`` function,
which is similar to that found in the ``six`` cross-version compatibility
module.::
    
    from mementos import MementoMetaclass, with_metaclass

    class Thing23(with_metaclass(MementoMetaclass, object)):
        ...

Careful with Call Signatures
============================

``MementoMetaclass`` caches on call signature, which can vary if keyword args
are used. E.g. ``def func(a, b=2)`` could be called ``func(1)``, ``func(1,2)``,
``func(a=1)``, ``func(1, b=2)``, or ``func(a=2, b=2)``--and all resolve to the
same logical call. And this is just for two parameters! If there are more than
one ``kwarg``, they can be arbitrarily ordered, creating *many* logically
identical permuations. Thank Goodness Python doesn't allow kwargs to come before
positional args, else there'd be even more ways to make the same call.
    
So if you instantiate an object once, then again with a logically identical call
but using a different calling structure/signature, the object won't be created
and cached just once--it will be created and cached multiple times.::
    
    o1 = Thing("lovely")
    o2 = Thing(name="lovely")
    assert o1 is not o2     # because the call signature is different
        
This may degrade performance, and can also create errors, if you're counting on
``mementos`` to create just one object. So don't do that. Use a consistent
calling style, and it won't be a problem.

In most cases, this isn't an issue, because objects tend to be instanitated with
a limited number of parameters, and you can take care that you instantiate them
with parallel call signatures. Since this works 99% of the time and has a simple
implementation, it's worth the price of this inelegance.
    
If you want only part of the initialization-time call signature (i.e. arguments
to ``__init__``) to define an object's identity/cache key, there are two
approaches. One is to use ``MementoMetaclass`` and design ``__init__`` without
superflous attributes, then create one or more secondary methods to add/set
useful-but-not-essential data. E.g.::

    class OtherThing(with_metaclass(MementoMetaclass, object)):
    
        def __init__(self, name):
            self.name = name
            self.color = None   # unset for now
            self.weight = None
            
        def set(self, color=None, weight=None):
            self.color = color or self.color
            self.weight = weight or self.weight
            return self
    
    ot1 = OtherThing("one").set(color='blue')
    ot2 = OtherThing("one").set(weight='light')
    assert ot1 is ot2
    assert ot1.color == ot2.color == 'blue'
    assert ot1.weight == ot2.weight == 'light'

Or you can just define your own memoizing metaclass, using the factory function
described below.

Visiting the Factory
====================

The first iteration of ``mementos`` defined a single metaclass. It's since been
reimplemented as a parameterized meta-metaclass. Cool, huh? That basically means
that it defines a function, ``memento_factory()`` that, given a metaclass name
and a function defining how cache keys are constructed, returns a corresponding
metaclass. ``MementoMetaclass`` is the only metaclass that the module
pre-defines, but it's easy to define your own memoizing metaclass.::

    from mementos import memento_factory, with_metaclass
    
    IdTracker = memento_factory('IdTracker',
                                lambda cls, args, kwargs: (cls, id(args[0])) )
                                
    class MyTracker(with_metaclass(IdTracker, object)):
        ...
        
        # object idenity is the object id of first argument to __init__
        # (and there must be one, else the args[0] reference => IndexError)

The first argument to ``memento_factory()`` is the name of the metaclass being
defined. The second is a callable (e.g. lambda expression or function object)
that takes three arguments: a class object, an argument ``list``, and a keyword
arg ``dict``. Note that there is no ``*`` or ``**`` magic--args passed to the
key function have already been resolved into basic data structures.

The callable must return a globally-unique, hashable key for an object. This key
will be stored in the ``_memento_cache``, which is a simple ``dict``.

When various arguments are used as the cache key/object identity, you may use a
``tuple`` that includes the class and arguments you want to key off of. This can
also help debugging, should you need to examine the ``_memento_cache`` cache
directly. But in cases like the ``IdTracker`` above, it's not mandatory that you
keep extra information around. The raw ``id(args[0])`` integer value would
suffice, as would a constructed string or other immutable, hashable value.

In cases where arguments are very flexible, or involve flexible data types,
a high powered hashing function such as that provided by
`SuperHash <http://pypi.python.org/pypi/SuperHash>`_ comes in extremely handy.
E.g.::

    from superhash import superhash
    
    SuperHashMeta = memento_factory('SuperHashMeta',
                                lambda cls, args, kwargs: (cls, superhash(args)) )

For the 1% edge-cases where multiple call variations must be
conclusively resolved to a unique canonical signature, that can be done on a
custom basis (based on the specific args). Or in Python 2.7 and 3.x, the
``inspect`` module's ``getcallargs()`` function can be used to create a generic
"call fingerprint" that can be used as a key. (See the tests for example code.)

Notes
=====

 *  ``mementos`` is not to be confused with `memento <http://pypi.python.org/pypi/memento>`_,
    which does something completely different.

 *  Mementos was originally derived from `an ActiveState recipe
    <http://code.activestate.com/recipes/286132-memento-design-pattern-in-python/>`_
    by Valentino Volonghi. While the current implementation quite different and
    the scope much broader, the availability of that recipe was what enabled
    this module and the growing list of modules that depend on mementos. This is
    what open source evolution is all about. Thank you, Valentino!
    
 *  It is safe to memoize multiple classes at the same time. They will all be stored in the same cache, but
    their class is a part of the cache key, so the values are distinct.
   
 *  This implementation is *not* thread-safe, in and of itself. If you're
    in a multi-threaded environment, consider wrapping object instantiation
    in a lock.
   
 *  Automated multi-version testing managed with 
    `pytest <http://pypi.python.org/pypi/pytest>`_
    and `tox <http://pypi.python.org/pypi/tox>`_. Successfully packaged for, and tested against, all late-model verions of
    Python (2.6, 2.7, 3.2, and 3.3), plus one (2.5) that isn't so very recent,
    and one (PyPy 1.9, based on Python 2.7.2) that is differently implemented.


Installation
============

::

    pip install mementos
    
To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install mementos
    
(You may need to prefix these with "sudo " to authorize installation. If they're
already installed, the ``--upgrade`` flag will be helpful; add it right before the
package name.)