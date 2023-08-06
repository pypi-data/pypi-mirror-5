Named HTML entities are much neater and much easier to comprehend
than numeric entities. And because they fall within the ASCII range,
they're much safer to use in multiple contexts than Unicode and its
various encodings (UTF-8 and such).

This module helps convert from numerical HTML entites and Unicode
characters that fall outside the normal ASCII range into named
entities.

Usage
=====

Python 2::
  
    from namedentities import named_entities, unescape
    
    u = u'both em\u2014and&#x2013;dashes&hellip;'
    ne = named_entities(u)
    print "named:  ", repr(ne)
    print "unicode:", repr(unescape(ne))
    
yields::

    named:  'both em&mdash;and&ndash;dashes&hellip;'
    unicode: u'both em\u2014and\u2013dashes\u2026'

You can do just about the same thing in Python 3, but you
have to use a ``print`` function rather than a ``print`` statement,
and prior to 3.3, you have to skip the ``u`` prefix that marks
a string literal as unicode to Python 2.x. (3.3 adds the ``u``
prefix back in as an optional, doesn't-really-do-anything feature
that nonetheless helps cross-version compatibility quite a bit.)

Recent Changes
==============

 * The ``unescape(text)`` API, while long present, is now available for
   easy external consumption. It converts strings with HTML entities 
   into strings with just Unicode.

 * Repackaged as a Python package, rather than independent modules.
 
 * Now successfully packaged for, and tests against, against Python
   2.6, 2.7, and 3.3, as well as PyPy 2.0.2 (based on 2.7.3).
   Automated multi-version testing managed with the wonderful `pytest
   <http://pypi.python.org/pypi/pytest>`_ and `tox
   <http://pypi.python.org/pypi/tox>`_.  Should also work under
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
