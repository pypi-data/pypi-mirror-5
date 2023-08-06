**************
Liskov Utility
**************
Utility to check if your subtypes pass supertypes tests.


Liskov Substitution is related in SOLID principles.
It has been formulated by Barbara Liskov and Jeanette Wing
in order to define more precisely the notion of subtypes.

For more details read: http://reports-archive.adm.cs.cmu.edu/anon/1999/CMU-CS-99-156.ps

To ensure a certain respect of Liskov Substittution principle in your program,
you can simply make your subtypes tests extends your supertypes tests, but
importing a supertype test directly in subtype file make the test
being recognized by unit tests runners and run it several times.

You can just import it in a function, but to not repeat this every time,
I've made a small util, wich offers 3 ways to declare a subtype test.

Each solution gives you different expressiveness depending on your preference:
  - "subtypeof" function which just import and return a class from a module given as string argument.
  - "behave_as" metaclass generator function which returns a metaclass from given modules
  - "can_substitute" decorator wich returns the class extending the modules given as arguments

---------------------------------------------------------------------

**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none
    
=============
Installation
=============

Simply install it from pypi::

  pip install liskov

or from sources::

  git clone git@github.com:apieum/liskov.git
  cd liskov
  python setup.py install
  
=====
Usage
=====

------------------------
Example 1 - "subtypeof":
------------------------
  Not so suitable when a subtype inherits of several supertypes.


.. code-block:: python

    from liskov import subtypeof

    class ScientificCalcTest(subtypeof('testCalc.BasicCalcTest'), subtypeof('testConvert.BaseConverterTest')):
      def test_it_is_a_subtype_of_BasicCalc(self):
        from testCalc import BasicCalcTest
        assert isinstance(self, BasicCalcTest)

      def test_it_is_a_subtype_of_BaseConverter(self):
        from testConvert import BaseConverterTest
        assert isinstance(self, BaseConverterTest)

------------------------
Example 2 - "behave_as":
------------------------

.. code-block:: python

    from liskov import behave_as

    class ScientificCalcTest(object):
      __metaclass__ = behave_as('testCalc.BasicCalcTest', 'testConvert.BaseConverterTest')

      def test_it_is_a_subtype_of_BasicCalc(self):
        from testCalc import BasicCalcTest
        assert isinstance(self, BasicCalcTest)

      def test_it_is_a_subtype_of_BaseConverter(self):
        from testConvert import BaseConverterTest
        assert isinstance(self, BaseConverterTest)


-----------------------------
Example 3 - "can_substitute":
-----------------------------

.. code-block:: python

    from liskov import can_substitute

    @can_substitute('testCalc.BasicCalcTest', 'testConvert.BaseConverterTest')
    class ScientificCalcTest(object):
      def test_it_is_a_subtype_of_BasicCalc(self):
        from testCalc import BasicCalcTest
        assert isinstance(self, BasicCalcTest)

      def test_it_is_a_subtype_of_BaseConverter(self):
        from testConvert import BaseConverterTest
        assert isinstance(self, BaseConverterTest)


===========
Development
===========

Fell free to give feedback or improvment.

Launch test::

  git clone git@github.com:apieum/liskov.git
  cd liskov
  nosetests --with-spec --spec-color
