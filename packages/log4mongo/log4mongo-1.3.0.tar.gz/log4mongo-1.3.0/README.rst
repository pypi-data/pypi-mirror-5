log4mongo-python
================
log4mongo-python is mongo database handler for python logging, part of log4mongo.org project.
log4mongo-python is using pymongo driver - http://github.com/mongodb/mongo-python-driver


Requirements
------------

- python 2.7+
- pymongo
- mongo database

For more information see *debian_requirements.txt* and *requirements.txt* files.

Configuration
-------------

Example handler python configuration: ::

 import logging
 from log4mongo.handlers import MongoHandler

 logger = logging.getLogger('test')
 logger.addHandler(MongoHandler(host='localhost'))
 logger.warning('test')


Contextual information
----------------------

It is possible to decorate you document with contextual information. There are tow approaches.

**1.) approach**
::

 import logging
 from log4mongo.handlers import MongoHandler

 handler = MongoHandler(host='localhost')
 logger = logging.getLogger('test')
 logger.addHandler(handler)
 logging.LoggerAdapter(logger, {'ip': '127.0.0.1'}).info('test')

**2.) approach**
::

 import logging
 from log4mongo.handlers import MongoHandler

 handler = MongoHandler(host='localhost')
 logger = logging.getLogger('test')
 logger.addHandler(handler)
 logger.info('test', extra={'ip': '127.0.0.1'})


As you can see, second approach is more straightforward and there is no need to use LoggerAdapter.


Capped collections
------------------

Capped collections are fixed-size collections that support high-throughput operations that insert, retrieve,
and delete documents based on insertion order. Capped collections work in a way similar
to circular buffers: once a collection fills its allocated space, it makes room for new documents
by overwriting the oldest documents in the collection.

Before switching to capped collections, read this document please: http://docs.mongodb.org/manual/core/capped-collections/

This behaviour is disabled by default. You can enable this behaviour in constructor with *capped=True*:
::

 import logging
 from log4mongo.handlers import MongoHandler

 handler = MongoHandler(host='localhost', capped=True)


Tests
-----

**Tested on evnironment**

- LinuxMint 15 Olivia 64-bit
- python 2.7.4
- pymongo 2.6.3
- mongod - db version v2.4.7, Mon Oct 28 12:15:05.831 git version: 0161738abf06c1f067b56a465b706efd6f4bf2aa
- python unittest

**Running tests**

Before you run the test you must start mongo database. You will do so by this command: ::

 $ mongod --dbpath /tmp/


To run the test run command: ::

 $ python test.py
 $ python setup.py test


Author
------

| char0n (Vladimír Gorej, CodeScale s.r.o.) 
| email: gorej@codescale.net
| web: http://www.codescale.net

References
----------
- http://www.mongodb.org/
- http://docs.python.org/library/logging.html
- http://github.com/mongodb/mongo-python-driver
- http://log4mongo.org
