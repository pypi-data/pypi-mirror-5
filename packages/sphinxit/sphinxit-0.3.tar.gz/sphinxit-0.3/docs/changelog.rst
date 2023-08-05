.. _changelog:

Changelog
=========

Version 0.2.1 (2012-11-06)
--------------------------

* Python 2.6 compatibility is back
* unittest2 explicit usage fix for 2.6

Version 0.2 (2012-11-02)
--------------------------

* Python 3 compatibility (thanks to `six` layer)
* `oursql` as MySQL layer (no more MySQLdb)
* Fixes in meta characters escaping
* The code is more polished and tested

Version 0.1.2 (2012-08-06)
--------------------------

* Connection on demand only (on the .process() execution).
* Threaded connections and locks.

Version 0.1.1 (2012-07-31)
--------------------------

* Enhanced tests for lexemes.
* Q objects should not work with !=, IN and BETWEEN conditions (Sphinx restriction). Fixed.
* :class:`Sphinxit.Snippets` accepts single string as the :attr:`data` argument. Results single snippet string in such case.

Version 0.1
-----------
Released on July 30th 2012

First public release, ready for production.