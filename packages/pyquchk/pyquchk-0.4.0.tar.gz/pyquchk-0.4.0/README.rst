`pyquchk` - random and serial testing
==========================================

:mod:`pyquchk` (abbreviated from Python QuickCheck) is the most comprehensive
and extensible, altrough easy-to-use, random and serial testing framework.
As you see from the name, it's inspired by
`Haskell QuickCheck <http://hackage.haskell.org/package/QuickCheck>`_,
but aims to provide much more capabilities.

Full documentation, including usage examples, is available at
`pythonhosted.org/pyquchk <http://pythonhosted.org/pyquchk/>`_.

Features
========

Already implemented
^^^^^^^^^^^^^^^^^^^

:mod:`pyquchk` combines two approaches to the arguments values generation in a
single framework:

* `QuickCheck <http://hackage.haskell.org/package/QuickCheck>`_-like (random)

  Random (fuzzy) testing runs a function for many randomly generated arguments
  values to make sure it's generally correct. Some features (both from the
  original QuickCheck and unique to :mod:`pyquchk`)

* `SmallCheck <http://hackage.haskell.org/package/smallcheck>`_-like (serial)

  Serial testing means that values are generated starting with some edge cases and
  small ones. This exhausts all possible values up to some "size" and is
  deterministic, in contrast to the random approach. Serial testing nicely
  complements the random one and so gives more confidence that the function tested
  is correct.

Other notable features include:

* a lot of configurable built-in generators for different value types
  (see :ref:`arbitraries` for the list of currently implemented generators)

* custom generators are supported, both for built-in types and user-created ones

* easy-to-write and read syntax for simple property checking as well as for full
  tests to be run with a framework (:mod:`nose` or :mod:`py.test` for example)

* :mod:`pyquchk` attempts to give you the smallest available counterexample,
  always performing shrinkg of the generated value (and if a value is found with
  serial testing, it's probably already minimal)

* ``assume`` function (allows so-called conditional properties and much more)

* Easy creation of Arbitraries combinations

  Examples: string from list; tuple with equally-sized strings.

Planned
^^^^^^^

:mod:`pyquchk` is in active development, and I have many features to implement
here:

- Option to check for ``exists``, not ``for_all``

- Tests timing

  Show time spent in pyquchk code and in tested function

- Support generators arguments depending on other generators values

  Something like ``forAll`` in original QuickCheck, but everything is to be defined as the function
  default arguments.
  Example: integer from the range ``[0:len(list)]``.

- Size support

  Generation function takes `size` parameter which increases *(from 0 to 1?)* from the first to
  the last test. Explore ``sized``, ``resize`` and so on from QuickCheck - whether they will fit here.

- Look for best way to express:

  - Modifiers like positive/negative/nonempty/...
  - Different numbers distributions like uniform/exponential/...
  - Structures like ``def f(a={int: [str_(...)]}, b=[float], c={'x': int, 'y': list})``

- Any use for Python 3 annotations?

- Better testing pyquchk itself

- Smart shrink from QuickCheck, SmartCheck

- Collect, classify, cover

  Not only boolean parameters (label/no label), but numerical as well.
  Example: difference between approximate function result and the exact one.

- Verbosity settings

- Print seed and allow to change it

- Don't fail fast

- Add timeout
