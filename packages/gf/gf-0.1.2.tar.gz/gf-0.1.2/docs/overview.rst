Overview
========

`gf` lets you write generic functions
`generic functions <http://en.wikipedia.org/wiki/Generic_function>`_
with multi-methods, that dispatch on all their arguments:

>>> from gf import generic, method
>>> add = generic()
>>> type(add)
<type 'function'>

Lets define `add` for two integers:

>>> @method(int, int)
... def add(n0, n1):
...     return n0 + n1

Lets test it:

>>> add(1, 2)
3

Calling `add` with instances of other types fails:

>>> add("Hello ", "World")
Traceback (most recent call last):
...
NotImplementedError: Generic '__main__.add' has no implementation for type(s): __builtin__.str, __builtin__.str

Of course `add` can also by defined for two strings:

>>> @method(basestring, basestring)
... def add(s0, s1):
...     return s0 + s1

Now our hello world example works:

>>> add("Hello ", "World")
'Hello World'

`add` can also be defined for a string and an integer:

>>> @method(basestring, int)
... def add(s, n):
...     return s + str(n)

Thus we can add a string and a number:

>>> add("You ", 2)
'You 2'

Changes
-------

A short sketch of teh chnages done in each release.

Release 0.1.2
~~~~~~~~~~~~~

The following was changed in Release 0.1.2:

  * Added a generic functions for :meth:`gf.Object.__call__`.
  * Added a :class:`gf.go.FinalizingMixin`.
  * :func:`gf.generic` now also accepts a type.
  * Improved the exception information for ambiguous calls.
  * Fixed some documentation glitches.

Release 0.1.1
~~~~~~~~~~~~~

This was the initial release.

