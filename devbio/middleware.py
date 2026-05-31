"""
devbio/middleware.py
--------------------
MaintenanceMiddleware
    When SiteSettings.maintenance is True, ALL non-staff users are redirected
    to the maintenance page for every URL except:
      - /maintenance/        (the maintenance page itself)
      - /siteadmin/          (so staff can turn maintenance off)
      - /admin/              (Django built-in admin)
      - /static/ and /media/ (assets must still load)

    Staff users (is_staff=True) bypass the block entirely so they can still
    log in, review the site, and turn maintenance mode off.
"""

from django.shortcuts import render
from django.conf import settings


BYPASS_PREFIXES = ('/maintenance/', '/siteadmin/', '/admin/', '/static/', '/media/')


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only block when maintenance is on
        try:
            from siteadmin.models import SiteSettings
            site = SiteSettings.load()
            maintenance = site.maintenance
        except Exception:
            maintenance = False

        if maintenance:
            # Staff always bypass
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)

            # Allowed paths bypass
            path = request.path_info
            if any(path.startswith(p) for p in BYPASS_PREFIXES):
                return self.get_response(request)

            # Everyone else sees the maintenance page
            return render(request, 'maintenance.html', {'site': site}, status=503)

        return self.get_response(request)
