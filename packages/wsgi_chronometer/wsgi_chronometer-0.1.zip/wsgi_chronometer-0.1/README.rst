WSGI_CHRONOMETER
================


WSGI middleware for chronometer wsgi application

.. image:: https://travis-ci.org/cyplp/wsgi_chronometer.png?branch=master
   :target: https://travis-ci.org/cyplp/wsgi_chronometer


Usage
-----

You can use in your wsgi app :

::

 from wsgi_chronometer import ChronoFilter
 from somewhere import SomeWsgiApp

 return ChronoFilter(SomeWsgiApp,  **{'separator': '*', 'fields': ['DATETIME', 'TIME']})(environ, start_response)

or in the .ini deployement file :

::

 [app:sample]
 use = egg:sample_app

 [pipeline:main]
 pipeline =
    chrono
    sample

 [filter:chrono]
 use = egg:wsgi_chronometer
 separator = -
 fields = REQUEST_METHOD PATH_INFO HTTP_USER_AGENT HTTP_X_FORWARDED_FOR HTTP_X_REAL_IP


.. TODO list of fields.
