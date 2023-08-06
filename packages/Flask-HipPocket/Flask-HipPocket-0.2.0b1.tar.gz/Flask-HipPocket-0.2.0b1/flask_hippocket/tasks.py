# -*- coding: utf-8 -*-
"""
    flask.ext.hippocket.tasks
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Sean Vieira.
    :license: MIT, see LICENSE for more details.
"""

from flask import Blueprint, Markup, request, render_template
from itertools import chain
from os import path
from pkgutil import walk_packages
from werkzeug.utils import import_string
from werkzeug.exceptions import default_exceptions, HTTPException


def autoload(app, apps_package="apps", module_name="routes", blueprint_name="routes", on_error=None):
    """Automatically load Blueprints from the specified package and registers them with Flask."""

    if not apps_package:
        raise ValueError("No apps package provided - unable to begin autoload")

    if isinstance(apps_package, basestring):
        package_code = import_string(apps_package)
    else:
        #: `apps_package` can be the already imported parent package
        #: (i.e. the following is a licit pattern)::
        #:
        #:      import app_package
        #:      # do something else with app_package
        #:      autoload(app, app_package)
        package_code = apps_package
        apps_package = apps_package.__name__

    package_paths = package_code.__path__

    package_paths = [path.join(app.root_path, p) for p in package_paths]
    root = apps_package
    apps_package = apps_package + u"." if not apps_package.endswith(".") else apps_package

    if on_error is None:
        on_error = lambda name: app.logger.warn("Unable to import {name}.".format(name=name))

    _to_import = "{base}.{module}.{symbol}"
    import_template = lambda base: _to_import.format(base=base,
                                                        module=module_name,
                                                        symbol=blueprint_name)

    #: Autoloaded apps must be Python packages
    #: The root of the package is also inspected for a routing file
    package_contents = chain([[None, root, True]],
                                walk_packages(path=package_paths, prefix=apps_package, onerror=on_error))
    for _, sub_app_name, is_pkg in package_contents:

        if not is_pkg:
            continue

        sub_app_import_path = import_template(base=sub_app_name)
        sub_app = import_string(sub_app_import_path)

        if isinstance(sub_app, Blueprint):
            app.register_blueprint(sub_app)
        else:
            app.logger.warn(("Failed to register {name} - "
                "it does not match the registration pattern.").format(name=sub_app_name))


def setup_errors(app, error_template="errors.html"):
    """Add a handler for each of the available HTTP error responses."""
    def error_handler(error):
        if isinstance(error, HTTPException):
            description = error.get_description(request.environ)
            code = error.code
            name = error.name
        else:
            description = error
            code = 500
            name = "Internal Server Error"
        return render_template(error_template,
                                code=code,
                                name=Markup(name),
                                description=Markup(description))

    for exception in default_exceptions:
        app.register_error_handler(exception, error_handler)
