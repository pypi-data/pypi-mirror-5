VERSION = (0, 2, 7, 'beta', 1)

def get_version():
    # Don't litter django_extras/__init__.py with all the get_version stuff.
    # Only import if it's actually called.
    from django_extras.utils.version import get_version
    return get_version(VERSION)
