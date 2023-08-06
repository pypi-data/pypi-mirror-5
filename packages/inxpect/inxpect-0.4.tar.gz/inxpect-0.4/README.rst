**************
Inxpect
**************

.. image:: https://pypip.in/v/inxpect/badge.png
        :target: https://pypi.python.org/pypi/inxpect


Intuitive inspect and expect



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

  pip install inxpect

or from sources::

  git clone git@github.com:apieum/inxpect.git
  cd inxpect
  python setup.py install

=========
Features
=========

* Build properties inspector from a type or object
* Can inspect objects recursively (default depth is 0)
* Defines a set of chainable expectations within properties types
* Provides a set of operators
* Each operator support is_true and is_false methods
* Can inject getters to operators and expectations constructors
* Can inject getter closures to expectations
* Getters, operators and expectations are serializables and searchables
* Expectations results are tunables (returns booleans, raises exceptions, log...)
* tested with python versions 2.7, 3.2 and 3.3

----------------------
Chainable expectations
----------------------

*Defaults*:

- equal_to, not_equal_to, same_as, not_same_as
- lower_than, lower_or_equal_than, greater_than, greater_or_equal_than
- type_is, type_is_not, instance_of, not_instance_of
- len, and, or
- operators symbols: ==, !=, >, >=, <, <=, '|' (for or), '&' (for and)

*Lists and Tuples*:

- has, has_all, has_any
- has_key, has_keys, has_any_key
- at

*Dict*:

- has_item, has_items, has_any_item
- has_key, has_keys, has_any_key
- has_value, has_values, has_any_value
- at


---------
Operators
---------

- Equal, NotEqual, SameAs, NotSameAs
- LowerThan, LowerOrEqualThan, GreaterThan, GreaterOrEqualThan
- TypeIs, TypeIsNot, InstanceOf, NotInstanceOf
- Contains, NotContains, ContainsAny, ContainsAll
- ContainsItem, ContainsAllItem, ContainsAnyItem
- ContainsValue, ContainsAllValue, ContainsAnyValue


*Quick example*

.. code-block:: python

  from inxpect.expect.operator import Equal
  from inxpect import And, Or

  equal_2 = Equal(2)
  assert  equal_2(2)
  assert equal_2(3) is False

  assert Equal.is_true(2, 2)
  assert Equal.is_false(2, 3)

  # You can use a getter function:
  mod_3 = lambda num: num % 3
  multiple_of_3 = Equal(0, mod_3)

  assert multiple_of_3(15)
  assert multiple_of_3(16) is False

  # chaining:
  mod_5 = lambda num: num % 5
  multiple_of_5 = Equal(0, mod_5)

  multiple_of_3_and_5 = And(multiple_of_3, multiple_of_5)
  multiple_of_3_or_5 = Or(multiple_of_3, multiple_of_5)

  assert multiple_of_3_and_5(15)
  assert multiple_of_3_or_5(16) is False

  multiple_of_4 = Equal(0, lambda num: num % 4)

  multiple_of_3_4_or_5 = multiple_of_3_or_5 | multiple_of_4

  assert multiple_of_3_4_or_5(16)

  # Testing and search (lambda is partially pickled):
  assert (multiple_of_5 == Equal(0, lambda num: num % 5))
  assert (multiple_of_5 == Equal(0, lambda num: num % 4)) is False


=====
Usage
=====
---------
Forewords
---------

Each example uses these 2 weird classes:


  .. code-block:: python

    class Subject(object):
      args = tuple()
      kwargs = dict()
      def __call__(self, event):
        self.args = event.args
        self.kwargs = event.kwargs
        event.result = False

    class EventData(object):
      name = 'event'
      subject = Subject()
      args = tuple()
      kwargs = dict()
      result = True

      def __init__(self, **kwargs):
        for attr, value in kwargs.items():
          setattr(self, attr, value)

-------
Inspect
-------

Nothing hard, just a function "expect_factory" wich take an object or a type as template
and returns an inspector wich contains properties named like ones of the given template.
Inspector properties are operations which helps to make expectations on objects
with same properties (name, and expected type) as template.


"expect_factory" takes an optional second argument (by default 0) to precise the depth of recursion.
Each property containing an object will be replaced by an inspector until depth, otherwise,
object become an "ExpectSame" object.


.. code-block:: python

  import inxpect

  expect = inxpect.expect_factory(EventData)
  assert hasattr(expect, 'result')
  assert hasattr(expect.subject, 'args') is False
  # with depth to 1:
  expect = inxpect.expect_factory(EventData, 1)
  assert hasattr(expect.subject, 'args')

------------------
Expect Basics
------------------

.. code-block:: python

  import inxpect

  expect = inxpect.expect_factory(EventData)

  name_is_event1 = expect.name.equal_to('event1')  # can be done with ==
  result_is_not_None = expect.result != None
  is_event1 = name_is_event1 & result_is_not_None

  event1 = EventData(name='event1')
  event2 = EventData(name='event2', result=None)

  assert result_is_not_None(event1)
  assert result_is_not_None(event2) is False

  assert name_is_event1(event1)
  assert name_is_event1(event2) is False

  log = []
  expected = 'Name %s is not "event1"'

  def is_event1_fails(chain, at, *args, **kwargs):
    # args and kwargs are same passed to is_event1:
    event = args[0]
    if at in expect.name.equal_to('event1'):
      log.append(expected % event.name)
    return False

  is_event1.on_fail(is_event1_fails)

  assert is_event1(event1)
  assert is_event1(event2) is False

  assert log[0] == expected % 'event2'


---------------
Expect Closures
---------------

As briefly seen, operators can take a getter argument.
That's what is done by inspect that use AttrByName getter to return an attribute by its name.

In addition to this, each assertion (equal_to...) can take a closure argument,
wich is a function that take getter result as argument and return the value to test.

Internally, this mecanism is used to provide 'at' and 'len' assertions,
the example above illustrate how 'len' functions.


.. code-block:: python

  import inxpect

  expect = inxpect.expect_factory(EventData)

  name_len_is_5 = expect.name.equal_to(5, len)

  event1 = EventData()
  event2 = EventData(name='0123456789')

  assert name_len_is_5(event1)
  assert name_len_is_5(event2) is False

  # the closure also encapsulate len for comparisons
  assert name_len_is_5 == expect.name.equal_to(5, len)

  ### Details:
  # Never use this but it shows how len is encapsulated

  # func is the internal varname, needed to compare bytecode
  func = len
  # Lambda permit to get bytecode from __code__ attibute
  func_len = lambda *args, **kwargs: func(*args, **kwargs)
  not_func_len = lambda *args, **kwargs: len(*args, **kwargs)

  assert (name_len_is_5 == expect.name.equal_to(5, func_len))
  # assert it compares bytecode
  assert (name_len_is_5 == expect.name.equal_to(5, not_func_len)) is False



--------------
Expect Should
--------------

In case default operators are not sufficient, you can define yours and use them easily with should.
An operator is a simple class that extends Operator (located in inxpect.expect.operator)
which need the class method "is_true(cls, given, expected)" to returns a boolean.



.. code-block:: python

  from inxpect.expect import Expect
  from inxpect.expect.operator import Operator

  class MultipleOf5(Operator):
      @classmethod
      def is_true(cls, given, expected):
          return given % 5 == expected


  expect = Expect()
  expected = 0
  multiple_of_5 = expect.should(MultipleOf5, expected)

  assert multiple_of_5(10)
  assert multiple_of_5(11) is False

  # Should provides also the negation:
  not_multiple_of_5 = expect.should_not(MultipleOf5, expected)

  assert not_multiple_of_5(11)


  # Should can take closure:
  divide_by_2 = lambda given: given / 2
  multiple_of_2_and_5 = expect.should(MultipleOf5, expected, divide_by_2)

  assert multiple_of_2_and_5(10)
  assert multiple_of_2_and_5(15) is False

  # Should syntactic sugar:
  is_10 = expect.should == 10
  assert is_10(10)
  assert is_10(11) is False
  # like expect:
  is_10 = expect == 10
  assert is_10(10)
  assert is_10(11) is False

  # at the difference that should can take a closure:
  mod_2 = lambda num: num % 2
  multiple_of_2 = expect.should == (0, mod_2)
  assert multiple_of_2(10)
  assert multiple_of_2(11) is False

  # unlike expect:
  weird_example = expect == (0, mod_2)
  assert weird_example(10) is False
  assert weird_example((0, mod_2))




===========
Development
===========

Fell free to give feedback or improvements.

Launch test::

  git clone git@github.com:apieum/inxpect.git
  cd inxpect
  nosetests --with-spec --spec-color




.. image:: https://secure.travis-ci.org/apieum/inxpect.png?branch=master
   :target: https://travis-ci.org/apieum/inxpect
