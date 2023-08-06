from django.conf import settings
from django.core.validators import validate_email
from email.utils import parseaddr
import sys


def is_pretty_from_address(input):
    name, email = parseaddr(input)
    validate_email(email)

    if name:
        return True
    else:
        return False


def get_app_versions():
    versions = {}

    for app in list(settings.INSTALLED_APPS) + ['django']:
        __import__(app)
        app = sys.modules[app]

        if hasattr(app, 'get_version'):
            get_version = app.get_version
            if callable(get_version):
                version = get_version()
            else:
                version = get_version
        elif hasattr(app, 'VERSION'):
            version = app.VERSION
        elif hasattr(app, '__version__'):
            version = app.__version__
        else:
            continue

        if isinstance(version, (list, tuple)):
            version = '.'.join(str(o) for o in version)

        name = app.__name__.split('.')[-1].replace('_', ' ').capitalize()
        versions[name] = version

    return versions
