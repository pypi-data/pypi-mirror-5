=================================
(Yet Another) Auto-Attribute Dict
=================================

An ``aadict`` is a python dict sub-class that allows attribute-style
access to dict items, e.g. ``d.foo`` is equivalent to ``d['foo']``.
``aadict`` also provides a few other helpful methods, such as ``pick``
and ``omit`` methods. Also, an ``aadict`` is more call chaining
friendly (e.g. methods such as `update` return ``self``) and is
pickle'able.


Project
=======

* Homepage: https://github.com/metagriffin/aadict
* Bugs: https://github.com/metagriffin/aadict/issues


TL;DR
=====

Install:

.. code-block:: bash

  $ pip install aadict

Use:

.. code-block:: python

  from aadict import aadict

  # attribute access
  d = aadict(foo='bar', zig=87)
  assert d.foo == d['foo'] == 'bar'

  # helper methods
  assert d.pick('foo') == {'foo': 'bar'}
  assert d.omit('foo') == {'zig': 87}

  # method chaining
  d2 = aadict(x='y').update(d).omit('zig')
  assert d2.x == 'y' and d2.foo == 'bar' and d2.zig is None

  # converting a dict to an aadict recursively
  d3 = aadict.d2ar(dict(foo=dict(bar='zig')))
  assert d3.foo.bar == 'zig'


Details
=======

The aadict module provides the following functionality:


aadict
------

An `aadict` object is basically identical to a `dict` object, with the
exception that attributes, if not reserved for other purposes, map to
the dict's items. For example, if a dict ``d`` has an item ``'foo'``,
then a request for ``d.foo`` will return that item lookup. aadicts
also have several helper methods, for example ``aadict.pick``. To
fetch the value of an item that has the same name as one of the helper
methods you need to reference it by item lookup,
i.e. ``d['pick']``. The helper methods are:

* **aadict.pick** instance method:

  Returns a new aadict, reduced to only include the specified
  keys. Example:

  .. code-block:: python

    d = aadict(foo='bar', zig=87, zag=['a', 'b'])
    assert d.pick('foo', 'zag') == {'foo': 'bar', 'zag': ['a', 'b']}

* **aadict.omit** instance method:

  Identical to the ``aadict.pick`` method, but returns the complement,
  i.e. all of those keys that are *not* specified. Example:

  .. code-block:: python

    d = aadict(foo='bar', zig=87, zag=['a', 'b'])
    assert d.omit('foo', 'zag') == {'zig': 87}

* **aadict.d2ar** class method:

  Recursively converts the supplied `dict` to an `aadict`, including
  all sub-list and sub-dict types. Due to being recursive, but only
  copying dict-types, this is effectively a hybrid of a shallow and
  a deep clone. Example:

  .. code-block:: python

    d = aadict.d2ar(dict(foo=dict(bar='zig')))
    assert d.foo.bar == 'zig'

  Without the recursive walking, the ``.bar`` attribute syntax
  would yield an AttributeError exception because d.foo would
  reference a `dict` type, not an `aadict`.

* **aadict.d2a** class method:

  Converts the supplied `dict` to an `aadict`. Example:

  .. code-block:: python

    d = aadict.d2a(dict(foo='bar'))
    assert d.foo == d['foo'] == 'bar'

  Note that this is identical to just using the constructor,
  but is provided as a symmetry to the ``aadict.d2ar`` class
  method, e.g.:

  .. code-block:: python

    d = aadict(dict(foo='bar'))
    assert d.foo == d['foo'] == 'bar'
