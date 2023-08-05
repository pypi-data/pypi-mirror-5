'''\
TinkerPy
========

This Python 2 and 3 package provides:

*   funtionality related to Python 2 versus 3
*   special dictionary implementations (:class:`AttributeDict`,
    :class:`ImmutableDict`)
*   the :func:`flatten` function to flatten data structures composed of
    iterables
*   some useful decorators (:func:`multi_decorator`, :func:`attribute_dict`)
*   SAX handlers


Python 2 vs. 3
--------------

.. autofunction:: py2or3

.. py:data:: STRING_TYPES

    For Python 2 this is the :func:`tuple` ``(str, unicode)``, in Python 3
    this is simply :func:`str`.


Iterator Types
--------------

.. autoclass:: AttributeDict
.. autoclass:: ImmutableDict
.. autofunction:: flatten


Decorators
----------

.. autofunction:: multi_decorator
.. autofunction:: namespace
.. autofunction:: attribute_dict


SAX Handlers
------------

.. autoclass:: LexicalHandler
.. autoclass:: DeclarationHandler
'''

import collections
import abc


# Python 2 vs. 3

def py2or3(py2, py3):
    '''\
    Returns one of the given arguments depending on the Python version.

    :param py2: The value to return in Python 2.
    :param py3: The value to return in Python 3.
    :returns: ``py2`` or ``py3`` depending on the Python version.
    '''
    import sys
    if sys.version_info[0] >= 3:
        return py3
    else:
        return py2


STRING_TYPES = py2or3(lambda:(str, unicode), lambda:str)()


# ITERATOR TYPES

class AttributeDict(dict):
    '''\
    A mapping like :class:`dict`, which exposes its values as attributes.

    It uses the ``__getattr__``, ``__delattr__`` and ``__setattr__`` hooks, so
    be aware of that when overriding these methods.

    If an attribute is retrieved which does not exist but who's name is a key
    in the dictionary, the dictionary value is returned.

    If an attribute is set/deleted who's name is a key in the dictionary, the
    dictionary entry is updated/deleted. Otherwise the attribute is
    created/deleted. Thus attribute values shadow attributes on
    setting/deleting attributes.

    Examples:

    >>> ad = AttributeDict((('foo', 1), ('bar', 2)))
    >>> print(ad.foo); print(ad.bar)
    1
    2
    >>> ad.foo = 3; print(ad.foo == ad['foo'])
    True
    >>> del ad['bar']
    >>> print(ad.bar)
    Traceback (most recent call last):
    AttributeError: 'bar'
    >>> print('bar' in ad)
    False
    >>> ad.bar = 2
    >>> print('bar' in ad)
    False
    '''
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, name, value):
        if name in self:
            self[name] = value
        else:
            dict.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            dict.__delattr__(self, name)


class ImmutableDict(collections.Mapping):
    '''\
    An immutable mapping that accepts the same constructor arguments as
    :class:`dict`.

    >>> immutable = ImmutableDict({'foo': 1, 'bar': 2})
    >>> print(immutable['foo'])
    1
    >>> del immutable['foo']
    Traceback (most recent call last):
    TypeError: 'ImmutableDict' object does not support item deletion
    >>> immutable['foo'] = 3
    Traceback (most recent call last):
    TypeError: 'ImmutableDict' object does not support item assignment
    '''
    __slots__ = ('_dict')

    def __init__(self, *args, **kargs):
        self._dict = dict(*args, **kargs)

    def __getitem__(self, name):
        return self._dict[name]

    def __contains__(self, name):
        return name in self._dict

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return self._dict.__iter__()


def flatten(obj, *flattening_configurations):
    '''\
    Flattens iterable data structures.

    :param obj: The object to flatten. It should be an iterable.

    :param flattening_configurations: An arbitrary number of *flattening
        configurations*. A flattening configuration is a 1- or 2-tuple
        containing callables with one argument. The first callable is a test,
        which should return :const:`True` if the configuration applies to the
        given object and :const:`False` otherwise. The second callable, if
        given, is used to flatten the given object. If it does not exist, it
        is assumed to be :const:`None`.

        If no flattening configuration is given, the following is used::

            (
                (lambda obj: isinstance(obj, collections.Mapping),
                    lambda obj: obj.values()),
                (lambda obj: (isinstance(obj, collections.Iterable)
                        and not isinstance(obj, STRING_TYPES)), )
            )

    :returns: A generator returning all descendants of all of elements of
        ``obj``.


    Flattening works as follows:

    1. For each element ``e`` in the object to flatten do:

        1. Iterate over the flattening configurations:

            * If the test (the first callable of the current configuration)
              returns :const:`True`, stop iterating over the configurations
              and memorize ``e`` is flattable. If the second callable exists
              and is not :const:`None`, assign ``e`` as the result of calling
              this callable with ``e``. Otherwise ``e`` is not modified and
              memorized as being not flattable.

            * Otherwise go to next configuration.

        2. If ``e`` is flattable, flatten it and yield each resulting element.
           Otherwise yield ``e``.


    This function flattens ``obj`` as just described, creating a generator
    returning each element of each flattable descendant of ``obj``.


    Examples:

    >>> mapping = {1: 'foo', 2: 'bar'}
    >>> iterable = ('Hello', 'World', mapping)
    >>> for e in flatten(iterable):
    ...     print(e)
    Hello
    World
    foo
    bar
    >>> flattening_configs = (
    ...     (lambda obj: isinstance(obj, collections.Mapping),
    ...         lambda obj: obj.keys(), ),
    ...     (lambda obj: (isinstance(obj, collections.Iterable)
    ...             and not isinstance(obj, STRING_TYPES)), ),
    ... )
    >>> tuple(flatten(iterable, *flattening_configs))
    ('Hello', 'World', 1, 2)
    '''
    if len(flattening_configurations) == 0:
        flattening_configurations = (
            (lambda obj: isinstance(obj, collections.Mapping),
                lambda obj: obj.values(), ),
            (lambda obj: (isinstance(obj, collections.Iterable)
                    and not isinstance(obj, STRING_TYPES)), )
        )
    def _flatten(*objects):
        for obj in objects:
            flattable = False
            for flattening_configuration in flattening_configurations:
                try:
                    test, conversion  = flattening_configuration
                except ValueError:
                    test = flattening_configuration[0]
                    conversion = None
                if test(obj):
                    if conversion is not None:
                        obj = conversion(obj)
                    flattable = True
                    break
            if flattable:
                for value in _flatten(*obj):
                    yield value
            else:
                yield obj
    return _flatten(obj)


# DECORATORS

def multi_decorator(*decorators):
    '''\
    Allows to create a decorator which applies a list of decorators to a
    target. The function returned applies the decorators in reverse order of
    ``decorators``, i.e. in the same order as decorators are written above
    their target.

    :param decorators: Each item must be a callable.
    :returns: a function which applies the decorators in reverse order of
        ``decorators``

    Examples:

    >>> def data_deco(name, data):
    ...     def decorator(target):
    ...         setattr(target, name, data)
    ...         return target
    ...     return decorator
    ...
    >>> metadata = multi_decorator(data_deco('title', 'Foo Bar'),
    ...     data_deco('content', 'Hello World!'))
    >>> @metadata
    ... class Data(object): pass
    >>> Data.title
    'Foo Bar'
    >>> Data.content
    'Hello World!'
    '''
    def decorator_func(target):
        for decorator in reversed(decorators):
            target = decorator(target)
        return target
    return decorator_func


def namespace(mapping, *names, **attributes):
    '''\
    Creates a function decorator which extends the namespace of the function
    it is applied to with entries from ``mapping``. Only global values are
    overridden.

    :arg mapping: The mapping containing namespace elements.
    :type mapping: mapping type
    :arg names: The names to define in the function namespace with values of
        the corresponding ``mapping`` entry. If none are given, all entries
        of ``mapping`` are added to the namespace (then it not only has to
        have the method :meth:`__getitem__` but must be a mapping conformant
        to :class:`collections.Mapping`).
    :name attributes: Named attributes which set entries on the namespace,
        possibly overriding entries from ``mappings``.

    Examples:

    >>> class StringGenerator(object):
    ...     def __getitem__(self, name):
    ...         return 'StringGen: ' + name
    ...
    >>> a = 1
    >>> @namespace(StringGenerator(), 'a', 'c', 'd', 'e', e='namespace e')
    ... def test(b, c=3):
    ...     print(a)
    ...     print(b)
    ...     print(c)
    ...     print(d)
    ...     print(e)
    ...
    >>> test(2)
    StringGen: a
    2
    3
    StringGen: d
    namespace e
    >>> @namespace(StringGenerator())
    ... def test():
    ...     print(a)
    ...
    Traceback (most recent call last):
    ValueError: If no names are given, the first argument must be a mapping.
    >>> @namespace(dict(a='namespace a', c='namespace c', d='namespace d'))
    ... def test(b, c=3):
    ...     print(a)
    ...     print(b)
    ...     print(c)
    ...     print(d)
    >>> test(2)
    namespace a
    2
    3
    namespace d
    '''
    def decorator(func):
        func_globals = dict(func.__globals__)
        if len(names) > 0:
            for name in names:
                func_globals[name] = mapping[name]
        else:
            if isinstance(mapping, collections.Mapping):
                for name in mapping:
                    func_globals[name] = mapping[name]
            else:
                raise ValueError('If no names are given, the first argument must be a mapping.')
        try:
            func_closure = func.__closure__
        except AttributeError:
            func_closure = func.func_closure
        for name in attributes:
            func_globals[name] = attributes[name]
        func = func.__class__(func.__code__, func_globals, func.__name__,
            func.__defaults__, func_closure)
        return func
    return decorator


def attribute_dict(target):
    '''\
    A decorator to create :class:`AttributeDict` instances from callables
    return values.

    :param target: The callable to be wrapped.
    :returns: A function which wraps ``target`` and returns an
        :class:`AttributeDict` from the return value of ``target``.

    Example:

    >>> @attribute_dict
    ... def Test(z):
    ...     def t(foo):
    ...         print(z)
    ...         print(foo)
    ...     return locals()
    ...
    >>> t = Test('foo')
    >>> t.z
    'foo'
    >>> t.t('bar')
    foo
    bar
    '''
    def wrapper(*args, **kargs):
        return AttributeDict(target(*args, **kargs))
    return wrapper



# SAX

class LexicalHandler(object):
    '''\
    A stub base class for a lexical handler (see
    :const:`xml.sax.handler.property_lexial_handler`).
    '''
    __metaclass__ = abc.ABCMeta

    def comment(self, content):
        '''Receive notification of a comment.'''
        pass

    def startCDATA(self):
        '''Receive notification of the beginning of CDATA section.'''
        pass

    def endCDATA(self):
        '''Receive notification of the end of CDATA section.'''
        pass


class DeclarationHandler(object):
    '''\
    A stub base class for a declaration handler (see
    :const:`xml.sax.handler.property_declaration_handler`).
    '''
    __metaclass__ = abc.ABCMeta

    def startDTD(self, name, public_id, system_id):
        '''Receive notification of the beginning of a DTD.'''
        pass

    def endDTD(self):
        '''Receive notification of the end of a DTD.'''
        pass

    def startEntity(self, name):
        '''Receive notification of the beginning of an entity.'''
        pass

    def endEntity(self, name):
        '''Receive notification of the end of an entity.'''
        pass


del abc