"""
devbio/context_processors.py
-----------------------------
Injects the SiteSettings singleton into every template as ``site_settings``.
The try/except guard ensures the app boots cleanly on a fresh database before
``python manage.py migrate`` has been run (prevents OperationalError on first
start when the siteadmin tables do not yet exist).
"""

def site_settings(request):
    try:
        from siteadmin.models import SiteSettings
        obj = SiteSettings.load()
    except Exception:
        obj = None
    return {'site_settings': obj}
