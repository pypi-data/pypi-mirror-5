Django Diazo
============

Integrate Diazo in Django using WSGI middleware and add/change themes
using the Django Admin interface.

The code is maintained on GitHub (https://github.com/Goldmund-Wyldebeast-Wunderliebe/django-diazo).

Installation
------------

settings.py

    INSTALLED_APPS = (
        ...
        'django_diazo',
        ...
    )

We highly recommend to use the following code as the first lines of your
settings file. It's just a good practice:

    import os

    PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))  # Level of manage.py
    BASE_DIR = os.path.dirname(PROJECT_DIR)  # Level of virtualenv

You might want to supply your Django application with an out-of-the-box
theme, probably also managed in a VCS.

Create a new app with a ``diazo.py`` file in its root. The contents of
this file is should be something like this:

    from django_diazo.theme import DiazoTheme, registry

    class BootstrapTheme(DiazoTheme):
        name = 'Bootstrap Theme'
        slug = 'bootstrap_theme'
    registry.register(BootstrapTheme)

To synchronize the built-in themes with the database/application run the
following command:

    python manage.py syncthemes

wsgi.py

    # Apply WSGI middleware here.
    from django_diazo.wsgi import DiazoMiddlewareWrapper
    application = DiazoMiddlewareWrapper(application)

Database (South migrations)

    python manage.py migrate django_diazo

Uploaded themes
---------------

By default, the .zip files that are uploaded are extracted in the media
folder. You might want to serve these files in debug mode. Add the
following to your ``urls.py``:

    if settings.DEBUG:
        urlpatterns += patterns('',
           url(r'^%s/themes/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), 'django.views.static.serve',
               {'document_root': os.path.join(settings.MEDIA_ROOT, 'themes'), 'show_indexes': True}),
        )

For production environments it is not recommended to serve files from
the media folder. This implementation only servers files in the
``themes`` folder within the media folder but it would be better to
serve these files using a web server and not via Django.

CodeMirror
----------

Download `CodeMirror <http://codemirror.net/>`__.

See https://pypi.python.org/pypi/django-codemirror-widget.

You may want to add the (unpacked) CodeMirror download folder to your
``STATICFILES_DIRS`` and run:

    python manage.py collectstatic

Specify ``CODEMIRROR_PATH`` in ``settings.py``.

``CODEMIRROR_PATH`` is the URI of CodeMirror directory like
``CODEMIRROR_PATH = r"javascript/codemirror"``. If you don't specify it,
it defaults to ``'codemirror'``.

CodeMirror download should be put there (unpacked).

Settings

-  ``CODEMIRROR_PATH``

   -  the URI of CodeMirror directory (your CodeMirror installation
      should live in ``{{ STATIC_URL }}/{{ CODEMIRROR_PATH }}``)

-  ``CODEMIRROR_MODE``

   -  the default mode which may be a string or configuration map
      (DEFAULT: 'javascript')
   -  Suggestion: ``'xml'``

-  ``CODEMIRROR_THEME``

   -  the default theme applied (DEFAULT: 'default')

-  ``CODEMIRROR_CONFIG``

   -  base mapping for the rest of the CodeMirror options (DEFAULT:
      ``{ 'lineNumbers': True }``)

Logging
-------

If you want logging of the errors that might occur in the Diazo
transformation, add the following to ``settings.py``:

    DIAZO_LOG_FILE = '/var/log/django_diazo.log'

    LOGGING = {
        'formatters': {
            ...
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            ...
        },
        'handlers': {
            ...
            'django_diazo_file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'verbose',
                'filename': DIAZO_LOG_FILE,
            },
            'console':{
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            ...
        },
        'loggers': {
            ...
            'django_diazo': {
                'handlers': ['django_diazo_file', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            ...
        },
    }
