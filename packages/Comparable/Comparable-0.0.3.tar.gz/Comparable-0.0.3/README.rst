Introduction
============

Comparable is a library providing abstract base classes that enable
subclasses to be compared for "equality" and "similarity" based on
their attributes.

.. NOTE::
   0.0.x releases are experimental; the APIs are still being designed.



Getting Started
===============

Requirements
------------

* Python 3
* ``setuptools`` and/or ``pip``


Installation
------------

Comparable can be installed with ``pip`` or ``easy_install``::

    pip install Comparable

Or directly from the source code::

    python setup.py install



Basic Usage
===========

After installation, abstract base classes can be imported from the package::

    python
    >>> import comparable
    comparable.__version__
    >>> from comparable import SimpleComparable, CompoundComparable

Comparable classes use '``==``' as the operation for "equality" and
'``%``' as the operation for "similarity". They may also override a
``threshold`` attribute to set the "similarity" ratio.


Simple Comparables
------------------

Simple comparable types must override the ``equality`` and
``similarity`` methods to return bool and Similarity objects,
respectively. See ``comparable.simple`` for examples.


Compound Comparables
--------------------

Compound comparable types contain multiple simple comparable types.
They must override the ``attributes`` property to define which
attributes should be used for comparison. See ``comparable.compund``
for examples.



Examples
========

Comparable includes many generic comparable types::

    python
    >>> from comparable.simple import Number, Text, TextEnum, TextTitle
    >>> from comparable.compound import Group

A basic script may look similar to the following::

    from comparable.simple import TextTitle
    from comparable import tools

    base = TextTitle("The Cat and the Hat")
    items = [TextTitle("cat & hat"), TextTitle("cat & the hat")]

    print("Equality: {}".format(base == items[0]))
    print("Similarity: {}".format(base % items[0]))

    print("Duplicates: {}".format(tools.duplicates(base, items)))