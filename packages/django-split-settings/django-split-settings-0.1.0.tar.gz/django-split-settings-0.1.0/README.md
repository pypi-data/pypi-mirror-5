django-split-settings
=====================

Organize Django settings into multiple files and directories. Easily override and modify settings. Use wildcards in settings file paths and mark settings files as optional.


Installation
------------

Install by using `pip`:

    pip install django-split-settings


Usage
-----

Replace your existing ``settings.py`` with a list of components that make up your Django settings. Preferably create a settings package that contains all the files.

The [GitHub repository](http://github.com/2general/django-split-settings) contains an example app.

Here's a minimal example:

```python
from split_settings.tools import optional, include

include(
    'components/base.py',
    'components/database.py',
    optional('local_settings.py'),

    scope=locals()
)
```

In the example, files ``base.py`` and ``database.py`` are included in that order from the subdirectory called ``components/``. ``local_settings.py`` in the same directory is included if it exists.

> **Note:** The local context is passed on to each file, so each following file can access and modify the settings declared in the previous files.


### Advanced example

Here's an example of the new ``settings/__init__.py`` that also takes into consideration whether the user has supplied another settings module as a command line parameter. It also offers two different ways to override settings in the local installation:

```python
from split_settings.tools import optional, include
import os
import socket

if os.environ['DJANGO_SETTINGS_MODULE'] == 'example.settings':
    # must bypass this block if another settings module was specified
    include(
        'components/base.py',
        'components/locale.py',
        'components/apps_middleware.py',
        'components/static.py',
        'components/templates.py',
        'components/database.py',
        'components/logging.py',

        # OVERRIDE SETTINGS

        # hostname-based override, in settings/env/ directory
        optional('env/%s.py' % socket.gethostname().split('.', 1)[0]),

        # local settings (do not commit to version control)
        optional(os.path.join(os.getcwd(), 'local_settings.py')),

        scope=locals()
    )
```

The example also tries to include a settings file with the current hostname from the ``env/`` directory for different configurations on each host.

Finally, it tries to locate ``local_settings.py`` from the working directory (usually the project root directory, assuming that you called ``manage.py runserver`` from there).

> **Tip:** If you're using Apache and mod_wsgi, you can set the working directory with the ``home`` option in the ``WSGIDaemonProcess`` directive.


Overriding settings
-------------------

Files on the inclusion list can override and modify the settings configured in the previous files. For example:

``components/base.py``:

```python
DEBUG = False
TEMPLATE_DEBUG = DEBUG

MIDDLEWARE_CLASSES = (
    # Your project's default middleware classes
)

INSTALLED_APPS = (
    # Your project's default apps
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'example',
        'USER': 'db_user',
        'PASSWORD': 'abc123',
        'HOST': '',
        'PORT': '',
    }
}

```

``local_settings.py``:

```python
# Use debug mode locally
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Add django-debug-toolbar
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar',)

# Use a different database password in development
DATABASES['default']['PASSWORD'] = 'password1'
```


Tips and tricks
---------------

  * You can use wildcards in file paths:

    ```python
    include(..., 'components/my_app/*.py', ...)
    ```

    _Note that files are included in the order that ``glob`` returns them, probably in the same order as what ``ls -U`` would list them. The files are NOT in alphabetical order._


Changelog
---------

### 0.1.0

  * Initial version