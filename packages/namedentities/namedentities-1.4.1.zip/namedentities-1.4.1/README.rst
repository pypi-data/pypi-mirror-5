When reading HTML, named entities are often neater and easier to comprehend than
numeric entities, Unicode (or other charset) characters, or a mixture of all of
the above. Because they fall within the ASCII range, entities are also much
safer to use in multiple contexts than Unicode and its various encodings (UTF-8
and such).

This module helps convert from numerical HTML entites and Unicode characters
that fall outside the normal ASCII range into named entities. Or, if you prefer,
it will help you go the other way, mapping all entities into Unicode. And if you
decide you want entities of the counting type, it will even help you go numeric.

Usage
=====

Python 2::
  
    from namedentities import *
    
    u = u'both em\u2014and&#x2013;dashes&hellip;'
    
    print "named:  ", repr(named_entities(u))
    print "numeric:", repr(numeric_entities(u))
    print "unicode:", repr(unicode_entities(u))
    
yields::

    named:   'both em&mdash;and&ndash;dashes&hellip;'
    numeric: 'both em&#8212;and&#8211;dashes&#8230;'
    unicode: u'both em\u2014and\u2013dashes\u2026'

You can do just about the same thing in Python 3, but you have to use a
``print`` function rather than a ``print`` statement, and prior to 3.3, you have
to skip the ``u`` prefix that in Python 2 marks string literals as being Unicode
literals. Python 3.3, however, allows the ``u`` marker as an optional feature;
it doesn't really do anything specific, because all Python 3 strings are
Unicode--but it sure helps with cross-version code compatibility. (You can use
the ``six`` cross-version compatibility library, as the tests do.)

Recent Changes
==============

 * The ``unescape(text)`` API changes all entities into Unicode characters.
   While long present, is now available for easy external consumption. It has an
   alias, ``unicode_entities(text)`` for parallelism with the other APIs.

 * Repackaged first as a Python package, rather than independent modules. Then,
   given my growing confidence in managing cross-version packages, the Python 2 and
   Python 3 implementation backends have been merged into a single backend.
 
 * Now successfully packaged for, and tests against, against Python
   2.6, 2.7, and 3.3, as well as PyPy 2.0.2 (based on 2.7.3).
   Automated multi-version testing managed with the wonderful `pytest
   <http://pypi.python.org/pypi/pytest>`_ and `tox
   <http://pypi.python.org/pypi/tox>`_.
   
 * Should also work under
   Python 2.5 and 3.2 releases, and PyPy 1.9, but those have been removed from
   "official support" because they are no longer supported in my
   testing environment. Time to upgrade!

Notes
=====

 * Doesn't attempt to encode ``&lt;``, ``&gt;``, or
   ``&amp;`` (or their numerical equivalents) to avoid interfering
   with HTML escaping.

 * This is basically a packaging of `Ian Beck's work
   <http://beckism.com/2009/03/named_entities_python/>`_. Thank you, Ian!

Installation
============

::

    pip install -U namedentities

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade namedentities
    
(You may need to prefix these with "sudo " to authorize installation.)
