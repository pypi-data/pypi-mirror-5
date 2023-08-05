=====
Infix
=====

.. image:: https://pypip.in/v/infix/badge.png
    :target: https://pypi.python.org/pypi/infix/
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/borntyping/python-infix.png
    :target: https://travis-ci.org/borntyping/python-infix
    :alt: Travis build status

A decorator that allows functions to be used as infix functions.

Infix operators are created and applied as such, and do not stop the function from being called normally::

    >>> from infix import shift_infix as infix
    ... 
    >>> @infix
    ... def plus(a, b):
    ...     return a + b
    ...
    >>> print(40 <<plus>> 2)
    42
    >>> print(plus(5, 5))
    10

Variant syntaxes
----------------

Multiple infix syntaxes are provided by the ``infix`` module::

    >>> @and_infix
    ... def is_before(a, b):
    ...     return a < b
    ...
    >>> print(1 &is_before& 5)
    True

    >>> @or_infix
    ... def minus(a, b):
    ...     return a - b
    ...
    >>> print(1 |minus| 2)
    -1

    >>> @xor_infix
    ... def until(start, stop):
    ...     return range(start, stop)
    ...
    >>> print(list(1 ^until^ 10))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

Custom syntaxes
----------------

Python has a large set of operators than could be overridden to provide the infix syntax, so instead of providing them all a ``custom_infix`` function is provided. It takes two parameters, the names of the left and right operator functions::

    >>> @custom_infix('__rmod__', '__mod__')
    ... def ate(a, b):
    ...     return (a == 7 and b == 9)
    ...
    >>> print(7 %ate% 9)
    True
    >>> print(6 %ate% 7)
    False

The left function should be a `right operand <http://docs.python.org/2/reference/datamodel.html#object.__radd__>`_, and the right functions should be a `left operand <http://docs.python.org/2/reference/datamodel.html#object.__add__>`_.

You should be careful to avoid using operands that the objects your functions will take may provide themselves (as the initial right operand is only called if the previous object does not provide for that operand).

Compatibility
-------------

Works on all major Python versions (2.6, 2.7, 3.2, 3.3).

Tests
-----

The tests in this README files are run using `doctest`_. To run the tests, run ''python infix.py'' - alternatively, use `tox`_ to run the tests on all compatible Python versions.

.. _doctest: http://docs.python.org/3/library/doctest.html
.. _tox: http://testrun.org/tox/

Licence
-------

Copyright (C) 2013 Sam Clements

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
