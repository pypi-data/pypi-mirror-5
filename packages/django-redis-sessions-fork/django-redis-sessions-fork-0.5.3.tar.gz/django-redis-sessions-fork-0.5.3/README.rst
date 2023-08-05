django-redis-sessions-fork
==========================

:info: Redis Session Backend For Django

.. image:: https://api.travis-ci.org/hellysmile/django-redis-sessions-fork.png
    :target: https://travis-ci.org/hellysmile/django-redis-sessions-fork
.. image:: https://coveralls.io/repos/hellysmile/django-redis-sessions-fork/badge.png?branch=master
    :target: https://coveralls.io/r/hellysmile/django-redis-sessions-fork?branch=master
.. image:: https://pypip.in/d/django-redis-sessions-fork/badge.png
.. image:: https://pypip.in/v/django-redis-sessions-fork/badge.png


installation
------------

run ``pip install django-redis-sessions-fork``

or alternatively download the tarball and run ``python setup.py install``

set ``redis_sessions.session`` as your session engine, like so

.. code-block:: python

    SESSION_ENGINE = 'redis_sessions.session'

optional settings

.. code-block:: python

    # all these options are defaults, you can skip anyone
    SESSION_REDIS_HOST = 'localhost'
    SESSION_REDIS_PORT = 6379
    SESSION_REDIS_DB = 0
    SESSION_REDIS_PASSWORD = None
    SESSION_REDIS_PREFIX = None

    # if you prefer domain socket connection
    # you can just add this line instead of SESSION_REDIS_HOST and SESSION_REDIS_PORT
    SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = '/var/run/redis/redis.sock'

    # you can also use redis from url
    SESSION_REDIS_URL = 'redis://localhost:6379/0'

if you one of happy `heroku.com <http://heroku.com/>`_ users

you can skip redis configuration at all

``django-redis-sessions-fork`` already have prefiguration for redis clouds

tests

.. code-block:: console

    pip install tox
    tox
