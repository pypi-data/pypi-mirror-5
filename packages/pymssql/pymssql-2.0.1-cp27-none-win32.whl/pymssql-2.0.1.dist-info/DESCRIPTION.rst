pymssql - DB-API interface to Microsoft SQL Server
==================================================

.. image:: https://travis-ci.org/pymssql/pymssql.png?branch=master
        :target: https://travis-ci.org/pymssql/pymssql

.. image:: https://pypip.in/d/pymssql/badge.png
        :target: https://crate.io/packages/pymssql

.. image:: https://pypip.in/v/pymssql/badge.png
        :target: https://crate.io/packages/pymssql

A simple database interface to `Microsoft SQL Server`_ (MS-SQL) for `Python`_
that builds on top of `FreeTDS`_ to provide a Python DB-API (`PEP-249`_)
interface to SQL Server.

.. _Microsoft SQL Server: http://www.microsoft.com/sqlserver/
.. _Python: http://www.python.org/
.. _PEP-249: http://www.python.org/dev/peps/pep-0249/
.. _FreeTDS: http://www.freetds.org/

Detailed information on pymssql is available on the website:

https://code.google.com/p/pymssql/

New development is happening on GitHub at:

https://github.com/pymssql/pymssql

There is a Google Group for discussion at:

https://groups.google.com/forum/?fromgroups#!forum/pymssql


Do you use pymssql?
-------------------

Can you take a minute and fill out this survey to help us prioritize development tasks?

https://www.surveymonkey.com/s/KMQ8BM5


Recent Changes
==============

Version 2.0.1 - 2013-10-27 - `Marc Abramowitz <http://marc-abramowitz.com/>`_
-----------------------------------------------------------------------------
* MANIFEST.in: Add "\*.rst" to prevent install error: "IOError: [Errno 2] No
  such file or directory: 'ChangeLog_highlights.rst'"

Version 2.0.0 - 2013-10-25 - `Marc Abramowitz <http://marc-abramowitz.com/>`_
-----------------------------------------------------------------------------
* First official release of pymssql 2.X (`Cython`_-based code) to `PyPI`_!
* Compared to pymssql 1.X, this version offers:

  * Better performance
  * Thread safety
  * Fuller test suite
  * Support for Python 3
  * Continuous integration via `Travis CI`_
  * Easier to understand code, due to `Cython`_

See `ChangeLog`_ for older history...

.. _PyPI: https://pypi.python.org/pypi/pymssql/2.0.0
.. _Travis CI: https://travis-ci.org/pymssql/pymssql
.. _Cython: http://cython.org/
.. _ChangeLog: https://github.com/pymssql/pymssql/blob/master/ChangeLog


