import os


def memoize(func):
    cache = {}

    def memory_func(*args, **kwargs):
        cache_key = args

        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)

        return cache[cache_key]

    memory_func.__doc__ = func.__doc__

    return memory_func


@memoize
def find_manage(basedir):
    """
    Returns the path to manage.py relative to `basedir`.
    """
    for root, dirs, files in os.walk(basedir):
        if 'manage.py' in files:
            return os.path.join(root, 'manage.py')


@memoize
def find_settings(basedir):
    """
    Returns the path to settings.py relative to `basedir`.
    """
    for root, dirs, files in os.walk(basedir):
        if 'settings.py' in files:
            return os.path.join(root, 'settings.py')


@memoize
def find_django_appname(basedir):
    """
    Returns the django application name.
    """
    for root, dirs, files in os.walk(basedir):
        if 'settings.py' in files:
            return root.split("/")[-1]
