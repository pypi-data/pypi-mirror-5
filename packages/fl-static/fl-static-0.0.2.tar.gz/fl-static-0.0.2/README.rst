FL-Static
=========

Serve production static files with Flask.
A Flask version of `DJ-Static <https://github.com/kennethreitz/dj-static>`_.


Usage
-----

::

    $ pip install fl-static

Configure your static assets in::

    from flask import Flask

    app = Flask(__name__)
    app.config.update(
        STATIC_ROOT='static',
        STATIC_URL='/static',
    )

Then, use the Cling middleware::

    from fl_static import Cling
    app = Cling(app)

You can use Werkzeug's local development server::

    app.run()

Jinja2 Magic
^^^^^^^^^^^^

``fl_static.Jinja2Magic`` extends ``static.StringMagic`` providing Jinja2
template support.

You can see it in action in ``example.py``.

License
-------
http://marksteve.mit-license.org
