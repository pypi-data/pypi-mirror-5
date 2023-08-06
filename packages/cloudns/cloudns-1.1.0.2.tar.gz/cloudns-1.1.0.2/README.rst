YY cloudns API python client
============================

This client is a python binding for the YY cloudns API.

Installation
------------

To install cloudns, simply:

.. code-block:: bash

   $ pip install cloudns


Quick Start
-----------

This client supports all functions defined in the API. To use those functions,
first create a User object, then call methods on it.

.. code-block:: pycon

   >>> import cloundns
   >>> u = cloundns.User('dw_foo', '8AFBE6DEA02407989AF4DD4C97BB6E25')
   >>> u.get_all_zones()
   ...
   >>> u.get_all_records('yyclouds.com')
   ...

Since most api function requires a zone to work on, you can create a zone from
a User and call methods on zone. Zone contains the most frequently used
functions from the API.

.. code-block:: pycon

   >>> z = u.zone('yyclouds.com')
   >>> z.create_record('test-foo', '8.8.8.8', 'tel')
   >>> z.get_records_by_name('test-foo')
   ...
   >>> z.delete_records_by_name('test-foo')
   ...

This client does very strict error checking. Everything from HTTP error to bad
response from cloudns server will raise an exception. All exceptions raised by
cloudns will be a subclass of CloudnsError.

.. code-block:: pycon

   >>> r = z.create_record('test-foo', '8.8.8.8', 'uni'); z.delete_record_by_id(r.rid)
   ... # Will raise exception. Pending record can not be deleted.


Documentation
-------------

Cloudns API documentation is available at
http://www.nsbeta.info/doc/YY-DNS-API.pdf

Cloudns python client documentation is available at
https://cloudns.readthedocs.org/


ChangeLog
---------

* v1.1.0.2 2013-08-31

  - package tested on python 2.6/2.7/3.3
  - bugfix: fix an import error on python 3.3

* v1.1.0.1 2013-08-13

  - initial release
