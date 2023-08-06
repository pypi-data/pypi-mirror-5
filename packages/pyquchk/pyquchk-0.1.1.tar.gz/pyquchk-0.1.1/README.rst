Introduction
============

pyquchk (abbreviated from Python QuickCheck) is and easy-to-use, extensible
random testing library. As you see from the name, it's inspired by Haskell QuickCheck, but the aim
is not only to implement all the useful features from it, but actually provide more capabilities.

Examples
========

Some examples to get the overall idea how to use it for testing:

::

    @qc
    def int_associativity(a=int, b=int, c=int):
        # this is correct
        assert a + (b + c) == (a + b) + c

    @qc
    def float_associativity(a=float, b=float, c=float):
        # this is wrong
        assert a + (b + c) == (a + b) + c

    @qc
    def float_list_sum(a=list_(length=int_(1, 20), elements=float_())):
        # this is wrong
        assert sum(a) == sum(reversed(a))

    @qc
    def float_list_sum(a=list_):
        # this is wrong, althrough the list consists of int only!
        assert sum(a) == sum(reversed(a))


You can put this in a file, add `from pyquchk import *` and run nosetests on this file
(other test runners were not tested). Then you see, that the first test passed, and other two didn't.
Futhermore, pyquchk will show you values for which they don't hold, and try to shrink them
(not optimal yet).

The last test case fails fast as a feature which I call 'edgecases generation' is implemented here:
a small number of edge cases defined in a generator are always tested first, and for lists they
include an empty list (plus some other values).

Further info
============

Also, you can quite easy add new arbitrary values generators and combine them, but I haven't written
a documentation about how to do this.

Complete documentation and more pre-defined generators coming soon!
