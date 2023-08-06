boolmerge - Tools for merging sorted iterables with boolean operators.
======================================================================

This module provides 4 efficient iterator types for merging sorted
iterables according to boolean operators (AND, NOT, OR, XOR),
in a lazy fashion. All code is written is C for performance reasons.

Installation
------------

    $ python setup.py install


Usage
-----

First import the module:

    >>> import boolmerge

All the iterator types have the same interface. They should be
called with two argument, each one being a sorted iterable
(be it of any kind), which items should be orderable.
If this is not the case, the result is undefined.

``boolmerge.andmerge`` returns an iterator which yields all items
present in both of the iterators it is given as arguments:

    >>> list(boolmerge.andmerge("acd", "abc"))
    ['a', 'c']

Note that the iteration will be faster if you pass the shortest
iterable as first argument.

``boolmerge.ormerge`` returns an iterator which yields all items
present in any of the iterators it is given as arguments:

    >>> list(boolmerge.ormerge("abcd", "cef"))
    ['a', 'b', 'c', 'd', 'e', 'f']

``boolmerge.notmerge`` returns an iterator which yields all items
present in the first iterator it is given as argument, but not in
the second:

    >>> list(boolmerge.notmerge("bdf", "abcf"))
    ['d']

``boolmerge.xormerge`` returns an iterator which yields all items
present in either of the iterators it is given as arguments, but
not in both:

    >>> list(boolmerge.xormerge("adf", "abcd"))
    ['b', 'c', 'f']
