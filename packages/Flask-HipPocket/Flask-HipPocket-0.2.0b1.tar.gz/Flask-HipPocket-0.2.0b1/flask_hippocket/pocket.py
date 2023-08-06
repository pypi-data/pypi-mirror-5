# -*- coding: utf-8 -*-
"""
    flask.ext.hippocket.pocket
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Sean Vieira.
    :license: MIT, see LICENSE for more details.
"""

from functools import wraps
from werkzeug import import_string, cached_property

from .tasks import autoload, setup_errors

__all__ = ("HipPocket", "LateLoader", "Mapper")


class HipPocket(object):
    """A wrapper around Flask to help make managing complex applications easier.

    Why not use Flask's :meth:`~flask.Flask.before_first_request` decorator? Because functions
    registered via that decorator are run on the first request (as opposed to *before* it).

    This extension fills the gap between Flask-Script and
    :meth:`~flask.Flask.before_first_request`.  It is for attaching functionality that needs
    to be run on the application itself (as opposed to Flask-Script which is used to
    run jobs *with* the application) but which might be too intensive to run in response
    to the first request.

    Alternately, because a flask is always better when you have something to carry it in.
    """

    def __init__(self, app=None, tasks=None):
        """:arg app: A :class:`~flask.Flask` instance.  If none is provided the :meth:`HipPocket.init_app`  method may be called later
        to initialize the Flask instance.

        :arg tasks: An iterable of callable objects. Each callable will be passed the app in turn.
        """

        self.tasks = tasks if tasks is not None else [autoload, setup_errors]
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Runs each of the tasks added via the :meth:`task` decorator."""

        for task in self.tasks:
            task(app)

    def task(self, func, *args, **kwargs):
        """A task is a unit of work to be performed by HipPocket on an initialized Flask app.

        All tasks must take the initialized app as their first argument.
        They can take any other arguments at all - these arguments must be provided to the
        :meth:`task` decorator during decoration.

        Examples::

            from flask import Flask
            from flask.ext.hippocket import HipPocket

            hip_pocket = HipPocket()

            @hip_pocket.task
            def do_something(app):
                # Do something with app

            @hip_pocket.task(an_arg, another_arg)
            def do_something_else(app, an_arg, another_arg):
                # Do something with app, an_arg and another_arg

            app = Flask(__name__)

            hip_pocket.init_app(app)

        .. note::
            The task decorator does not handle single callable arguments. If you need
            to pass single callables pass it as a keyword argument.

        An example::

            # This will fail
            @hip_pocket.task(lambda x: x*2)
            def schedule_doubles(app, doubler):
                # Have the manager schedule something.

            # This will work as anticipated
            @hip_pocket.task(butler=lambda garment: garment.add_pocket_squares())
            def add_pocket_squares(app, butler):
                # Add pocket squares to the appropriate garments.
        """
        def decorator(f):
            @wraps(f)
            def inner(app):
                return f(app, *args, **kwargs)
            return inner

        if not callable(func) or len(args) > 0 or len(kwargs) > 0:
            def wrapper(func):
                task = decorator(func)
                self.tasks.append(task)
                return task
            return wrapper
        else:
            task = decorator(func)
            self.tasks.append(task)
            return task


class LateLoader(object):
    """Provides a way of loading views on the first request for the view
    rather than on application initialization.  This speeds up application load times
    and keeps resource requirements low (since you don't load code until you need it).

    Taken directly from the example in `Flask's docs <http://flask.pocoo.org/docs/patterns/lazyloading/>`__"""
    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit(u".", 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


class Mapper(object):
    """Provides a convenience wrapper around :class:`~flask.ext.hippocket.pocket.LateLoader`.

    It is designed to be used as follows::

        from flask import Blueprint
        from flask.ext.hippocket import Mapper

        routes = Blueprint("my_blueprint", __name__, url_prefix="/my-blueprint")
        mapper = Mapper(routes, "apps_package.my_app")

        mapper.add_url_rule("/", "my_module.my_endpoint")

    ``apps_package.my_app.my_module.my_endpoint`` will be imported
    when the URL ``/my-blueprint/`` is hit for the first time.
    This import will be cached in order to ensure that
    subsequent requests to this url will **not** result in additional imports."""
    def __init__(self, blueprint, base_import_name=None, **url_defaults):
        self.blueprint = blueprint
        self.url_defaults = url_defaults
        self.base_import_name = base_import_name \
            if base_import_name is not None \
            else blueprint.import_name

    def add_url_rule(self, url, import_name, **url_kwargs):
        """Add a URL to the wrapped :class:`~flask.Flask` or :class:`~flask.Blueprint`'s URL map."""

        import_path = u".".join([self.base_import_name, import_name])
        view = LateLoader(import_path)

        url_defaults = self.url_defaults.copy()
        url_defaults.update(**url_kwargs)
        url_kwargs = url_defaults

        self.blueprint.add_url_rule(url, view_func=view, **url_kwargs)

    #: :meth:`add` is an alias for :meth:`add_url_rule`.
    add = add_url_rule
