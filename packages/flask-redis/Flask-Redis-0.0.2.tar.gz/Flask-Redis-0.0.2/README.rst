Flask-Redis
===========

Add Redis Support to Flask.

Built on top of `redis-py <https://github.com/andymccurdy/redis-py>`_.

Currently a single namespace within the configuration is supported.

.. code-block:: python

    REDIS_URL="redis://localhost"

with the Redis instance automatically loading config from this namespace.

In the future, the ability to declare multiple Redis namespaces will be available

.. code-block:: python

    REDIS_CACHE_URL="redis://localhost/0"
    REDIS_METRICS_URL="redis://localhost/0"

    redis_cache = Redis(config_prefix="REDIS_CACHE")
    redis_metrics = Redis(config_prefix="REDIS_METRICS")

Installation
------------

.. code-block:: bash

    pip install flask-redis

Or if you *must* use easy_install:

.. code-block:: bash

    alias easy_install="pip install $1"
    easy_install flask-redis


Configuration
-------------

Your configuration should be declared within your Flask config. You can declare
via a Redis URL

.. code-block:: python

    REDIS_URL = "redis://:password@localhost:6379/0"

or you are able to declare the following

.. code-block:: python

    REDIS_HOST = "localhost"
    REDIS_PASSWORD = "password"
    REDIS_PORT = 6379
    REDIS_DATABASE = 5

To create the redis instance within your application

.. code-block:: python

    from flask import Flask
    from flask_redis import Redis

    app = Flask(__name__)
    redis_store = Redis(app)

or

.. code-block:: python

    from flask import Flask
    from flask_redis import Redis

    redis_store = Redis()

    def create_app():
        app = Flask(__name__)
        redis_store.init_app(app)
        return app

Usage
-----

.. code-block:: python

    from core import redis_store

    @app.route('/')
    def index():
        return redis_store.get('potato','Not Set')

**Protip:** The `redis-py <https://github.com/andymccurdy/redis-py>`_ package currently holds the 'redis' namespace,
so if you are looking to make use of it, your Redis object shouldn't be named 'redis'.

For detailed instructions regarding the usage of the client, check the `redis-py <https://github.com/andymccurdy/redis-py>`_ documentation.

Advanced features, such as Lua scripting, pipelines and callbacks are detailed within the projects README.
