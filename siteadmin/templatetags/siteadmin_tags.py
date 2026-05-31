from django import template
from siteadmin.models import SiteSettings

register = template.Library()

@register.simple_tag
def get_site_settings():
    try:
        return SiteSettings.load()
    except Exception:
        return None
