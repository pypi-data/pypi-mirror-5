import imp

from sirep.base import Report

_registry = {}

def register(slug, cls):
    _registry[slug] = cls

def get_report(slug):
    try:
        return _registry[slug]
    except KeyError:
        raise Exception("No such report '%s'" % slug)

def all_reports():
    return _registry.items()

def autodiscover():
    from django.conf import settings
    REPORTING_SOURCE_FILE =  getattr(settings, 'REPORTING_SOURCE_FILE', 'reports')
    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        try:
            imp.find_module(REPORTING_SOURCE_FILE, app_path)
        except ImportError:
            continue
        __import__('%s.%s' % (app, REPORTING_SOURCE_FILE))
