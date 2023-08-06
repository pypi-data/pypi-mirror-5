Flask-Heroku-Auth
=================

.. image:: https://travis-ci.org/rhyselsmore/flask-heroku-auth.png?branch=master
        :target: https://travis-ci.org/rhyselsmore/flask-heroku-auth

.. image:: https://pypip.in/d/Flask-Heroku-Auth/badge.png
        :target: https://crate.io/packages/Flask-Heroku-Auth/

A set of Flask Route decorators to enable either Session-Based Authentication
via Heroku's OAuth mechanism, or Basic Stateless Authentication via Heroku's
API Key facilities.

Installation
------------

.. code-block:: bash

    pip install flask-heroku-auth

Configuration
-------------

To enable regex routes within your application

.. code-block:: python

    from flask import Flask
    from flask_heroku_auth import HerokuAuth

    app = Flask(__name__)
    HerokuAuth(app)

or

.. code-block:: python

    from flask import Flask
    from flask_heroku_auth import HerokuAuth

    auth = HerokuAuth()

    def create_app():
        app = Flask(__name__)
        auth.init_app(app)
        return app

From here, it is a matter of decorating the appropriate routes.

For example, the following would implement authentication via the Heroku
OAuth facility

.. code-block:: python

    @app.route('/')
    @auth.oauth
    def index():
        return "Ok"

On the other hand, you may wish to authenticate via the Heroku API Key
facility. In this case, the credentials are sent through with every
request as an 'Authorization' header

.. code-block:: python

    @app.route('/')
    @auth.api
    def index():
        return "Ok"

You can also restrict access to a Heroku user who has an @heroku.com email
address.

.. code-block:: python

    @app.route('/')
    @auth.oauth
    @auth.herokai_only
    def index():
        return "Ok"
