"""
URL configuration for devbio.

Media files are served by our custom ``serve_media`` view which works
correctly in both DEBUG=True (development) and DEBUG=False (production)
without requiring a web-server rewrite rule.
"""

from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings

from accounts.views import signup, logout_view
from public.views import profile, home
from dashboard.views import (
    dashboard, edit_profile, edit_theme, edit_premium_profile,
    add_link, edit_link, delete_link,
)
from django.contrib.auth import views as auth_views
from devbio.media_serve import serve_media

urlpatterns = [
    # ── Django built-in admin ─────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Custom site admin panel ───────────────────────────────────────
    path('siteadmin/', include('siteadmin.urls')),

    # ── Dashboard ────────────────────────────────────────────────────
    path('dashboard/',                           dashboard,    name='dashboard'),
    path('dashboard/edit/',                      edit_profile, name='edit_profile'),
    path('dashboard/theme/',                     edit_theme,        name='edit_theme'),
    path('dashboard/style/',                     edit_premium_profile, name='edit_premium_profile'),
    path('dashboard/add-link/',                  add_link,     name='add_link'),
    path('dashboard/edit-link/<int:link_id>/',   edit_link,    name='edit_link'),
    path('dashboard/delete-link/<int:link_id>/', delete_link,  name='delete_link'),

    # ── Public profile ───────────────────────────────────────────────
    path('@<str:username>/', profile, name='profile'),

    # ── Auth ─────────────────────────────────────────────────────────
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html'),
        name='login',
    ),
    path('signup/', signup,      name='signup'),
    path('logout/', logout_view, name='logout'),

    # ── Home ─────────────────────────────────────────────────────────
    path('', home, name='home'),
    path('maintenance/', home, name='maintenance'),  # served by middleware

    # ── Media files (works in DEBUG=True and DEBUG=False) ────────────
    re_path(r'^media/(?P<path>.+)$', serve_media, name='media'),
]
