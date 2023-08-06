Flask-PJAX
==========


.. image:: https://travis-ci.org/rhyselsmore/flask-pjax.png?branch=master
        :target: https://travis-ci.org/rhyselsmore/flask-pjax

.. image:: https://pypip.in/d/Flask-PJAX/badge.png
        :target: https://crate.io/packages/Flask-PJAX/

Add a fairly basic handler for PJAX to Flask.

Allows you to specify a base template for both a normal request or a
PJAX request. This allows you to return the required code blocks, and
choose what you wish to render.

Installation
------------

.. code-block:: bash

    pip install flask-pjax

Configuration
-------------

Configiguring Flask-PJAX is fairly simple. To get started, initalise it against
your application.

.. code-block:: python

    from flask import Flask
    from flask_pjax import PJAX

    app = Flask(__name__)
    PJAX(app)

or

.. code-block:: python

    from flask import Flask
    from flask_pjax import PJAX

    app = Flask(__name__)
    pjax = PJAX(app)

or

.. code-block:: python

    from flask import Flask
    from flask_pjax import PJAX

    pjax = PJAX()

    def create_app():
        app = Flask(__name__)
        pjax.init_app(app)
        return app

Currently, the base template for your PJAX request is the only configuration
item. This is set to the location of the template within your project.

.. code-block:: python

    PJAX_BASE_TEMPLATE = "pjax.html"

Usage
-----

You can return your templates like you normally do.

.. code-block:: python

    # app.py

    @app.route('/')
    def index():
        return render_template('index.html')

Your base template remains the same.

.. code-block:: html

    # base.html

    <html>
    <head>
        <title>Woop</title>
    </head>
    <body>
        {% block content %}{% endblock %}
    </body>
    </html>

And you create a PJAX base template.

.. code-block:: html

    # pjax.html

    <title>Woop</title>

    {% block content %}{% endblock %}

And within your index template, you can specify your base template:

.. code-block:: html

    # index.html

    {% extends pjax('base.html') %}

    <title>Woop - Home</title>

    {% block content %}
    This is my homepage
    {% endblock %}

This will render the pjax.html for PJAX requests, and the base for non-PJAX requests.

Furthermore, you can specify a custom PJAX Base Template:

.. code-block:: html

    {% extends pjax('base.html', pjax='/base/custom_pjax_template') %}

Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug. There is a Contributor Friendly tag for issues that should be ideal for people who are not very familiar with the codebase yet.
#. Fork `the repository`_ on Github to start making your changes to the **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.

.. _`the repository`: http://github.com/rhyselsmore/flask-pjax