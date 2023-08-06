=============================
greencard
=============================

.. image:: https://badge.fury.io/py/greencard.png
    :target: http://badge.fury.io/py/greencard
    
.. image:: https://travis-ci.org/Nekroze/greencard.png?branch=master
        :target: https://travis-ci.org/Nekroze/greencard

.. image:: https://pypip.in/d/greencard/badge.png
        :target: https://crate.io/packages/greencard?version=latest

Documentation
-------------

The full documentation is at http://greencard.rtfd.org.

Quickstart
----------

Install greencard::

    pip install greencard

Then you can use the ``GreenCard`` decorator on your unittests to provide them
with each and every card in the library::

    from unittest import TestCase
    from greencard.decorator import GreenCard

    class CardTests(TestCase):
        @GreenCard('mylibrary.lbr')
        def execute(self, card):
            self.assertTrue(0 < card.code <= 1000)

The above will test each and every card in the database stored at
``mylibrary.lbr`` and ensure that their code is higher then 0 but no higher
then 1000.

Features
--------

* Unittest decorator that provides a database of cards one at a time on test.
