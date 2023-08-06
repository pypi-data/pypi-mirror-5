**************
Liskov Utility
**************

.. image:: https://pypip.in/v/liskov/badge.png
        :target: https://pypi.python.org/pypi/liskov

Utility to check if your subtypes pass supertypes tests.


Liskov Substitution is related in SOLID principles.
It has been formulated by Barbara Liskov and Jeanette Wing
in order to define more precisely the notion of subtypes.

For more details read: http://reports-archive.adm.cs.cmu.edu/anon/1999/CMU-CS-99-156.ps

To ensure a certain respect of Liskov Substitution principle in your program,
you can simply make your subtypes tests extends your supertypes tests, but
importing a supertype test directly in subtype file make the test
being recognized by unit tests runners and run it several times.

You can just import it in a function, but to not repeat this every time,
I've made a small util, wich offers 3 ways to declare a subtype test.

Each solution gives you different expressiveness depending on your preference:
  - "subtype" function which just import and return a class from a module given as string argument.
  - "behave_as" metaclass generator function which returns a metaclass from given modules.
  - "can_substitute" decorator wich returns the class extending modules given as arguments.

Liskov and Wing classified subtype relationships in two broad categories:
  - Extension subtypes: add methods or eventually states to supertypes
  - Constrained subtypes: when supertype enable variations in subtypes

Since version 0.2 you can find some helpers to define constraints.(see example 4)

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
Example 1 - "subtype":
------------------------
  Use a lambda if too long.


.. code-block:: python

    from liskov import subtype

    BasicCalc = lambda: subtype('testCalc.BasicCalcTest')
    BaseConverter = lambda: subtype('testConvert.BaseConverterTest')
    class ScientificCalcTest(BasicCalc(), BaseConverter()):
      def test_it_is_a_subtype_of_BasicCalc(self):
        from testCalc import BasicCalcTest
        assert isinstance(self, BasicCalcTest)

      def test_it_is_a_subtype_of_BaseConverter(self):
        from testConvert import BaseConverterTest
        assert isinstance(self, BaseConverterTest)

------------------------
Example 2 - "behave_as":
------------------------
*Python 2 version*

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



*Python 3 version*

.. code-block:: python

    from liskov import behave_as

    metaclass = behave_as('testCalc.BasicCalcTest', 'testConvert.BaseConverterTest')

    class ScientificCalcTest(object, metaclass=metaclass):
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


-----------------------------
Example 4 - Constraints:
-----------------------------

This example follow Liskov and Wing constrained subtypes Elephants hierarchy example
from "Behavioural Subtyping using invariants and constraints" (link above)

Elephants can be white, green or blue
RoyalElephant is always blue
AlbinoElephant is always white

Each instance of Elephant in ElephantTest is made with "new_elephant"
ElephantTest test if an Elephant can be white, green or blue.


*Declare Constraints with a decorator*


.. code-block:: python

    from liskov import can_substitute, under_constraint
    import elephant

    @can_substitute('elephant.ElephantTest')
    @under_constraint('test_it_can_be_grey', 'test_it_can_be_white')
    class RoyalElephantTest(object):
      def new_elephant(self, *args):
        return elephant.RoyalElephant()


*Declare Constraints with metaclass*

Python 2 version

.. code-block:: python

    from liskov import behave_as
    import elephant

    class RoyalElephantTest(object):
      __metaclass__ = behave_as('elephant.ElephantTest').except_for('test_it_can_be_grey', 'test_it_can_be_white')
      def new_elephant(self, *args):
        return elephant.RoyalElephant()



Python 3 version

.. code-block:: python

    from liskov import behave_as
    import elephant

    metaclass = behave_as('elephant.ElephantTest').except_for('test_it_can_be_grey', 'test_it_can_be_white')
    class RoyalElephantTest(object, metaclass=metaclass):
      def new_elephant(self, *args):
        return elephant.RoyalElephant()


*Declare Constraints with subtype function*
  bind "subtype" to "constrain" with any of these operators: "& | + -"

.. code-block:: python

    from liskov import subtype, constrain
    import elephant

    ConstrainedElephantTest = lambda: subtype('elephant.ElephantTest') & constrain('test_it_can_be_grey', 'test_it_can_be_white')

    class RoyalElephantTest(ConstrainedElephantTest()):
      def new_elephant(self, *args):
        return elephant.RoyalElephant()


===========
Development
===========

Fell free to give feedback or improvment.

Launch test::

  git clone git@github.com:apieum/liskov.git
  cd liskov
  nosetests --with-spec --spec-color


.. image:: https://secure.travis-ci.org/apieum/liskov.png?branch=master
   :target: https://travis-ci.org/apieum/liskov
