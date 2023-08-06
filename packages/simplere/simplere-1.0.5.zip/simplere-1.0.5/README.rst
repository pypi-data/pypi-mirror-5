.. image:: https://travis-ci.org/jonathaneunice/simplere.png?branch=master
    :target: https://travis-ci.org/jonathaneunice/simplere

.. image:: https://pypip.in/d/simplere/badge.png
    :target: https://crate.io/packages/simplere/

A simplified interface to Python's regular expression (``re``)
string search that tries to eliminate steps and provide
simpler access to results. As a bonus, also provides compatible way to
access Unix glob searches.

Usage
=====

Python regular expressions are powerful, but the language's lack
of an *en passant* (in passing) assignment requires a preparatory
motion and then a test::

    import re
    
    match = re.search(pattern, some_string)
    if match:
        print match.group(1)

With ``simplere``, you can do it in fewer steps::

    from simplere import *

    if match / re.search(pattern, some_string):
        print match[1]

That's particularly valuable in complex search-and-manipulate
code that requires multiple levels of searching along with
pre-conditions, error checking, and post-match cleanup, formatting,
and actions.

As a bonus,
``simplere`` also provides simple glob access.::

    if 'globtastic' in Glob('glob*'):
        print "Yes! It is!"
    else:
        raise ValueError('OH YES IT IS!')

See `Read the Docs <http://simplere.readthedocs.org/en/latest/>`_
for the full installation and usage documentation.
