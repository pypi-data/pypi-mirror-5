=============================
Librator
=============================

.. image:: https://badge.fury.io/py/librator.png
    :target: http://badge.fury.io/py/librator
    
.. image:: https://travis-ci.org/Nekroze/librator.png?branch=master
        :target: https://travis-ci.org/Nekroze/librator

.. image:: https://pypip.in/d/librator/badge.png
        :target: https://crate.io/packages/librator?version=latest


A method of automatically constructing a Librarian library database from a directory of yaml files or the reverse.

Documentation
-------------

The full documentation is at http://librator.rtfd.org.

Quickstart
----------

Install Librator::

    pip install librator

Then start creating cards with::

    libratorcard cards/mycard

When you have your directory of card files simple pack then up::

    librator cards/ library.lbr

Features
--------

* Turns a collection of yml based card files into a librarian card database.
* Can turn a librarian card database into a directory of yml based card files.
* Provides a tool for creating an empty example card file.
