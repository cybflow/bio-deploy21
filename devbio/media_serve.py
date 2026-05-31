"""
devbio/media_serve.py
---------------------
A minimal, production-safe media-file streaming view.

Why this exists
~~~~~~~~~~~~~~~
Django's ``static()`` URL helper (used in urls.py) only registers the
``django.views.static.serve`` view when ``DEBUG=True``.  In production
(``DEBUG=False``) those URL patterns disappear, so uploaded files
(avatars, background images) return 404.

The correct production approach is to have a real web server (nginx,
Caddy) serve MEDIA_ROOT under MEDIA_URL.  However, for self-hosted
single-process deployments (gunicorn without a front-end proxy) we
provide this lightweight streaming view that:

  1. Resolves the requested path relative to ``MEDIA_ROOT``.
  2. Rejects any path that would escape MEDIA_ROOT (path traversal guard).
  3. Guesses the MIME type from the file extension.
  4. Streams the file in 64 KB chunks — avoids loading entire images into
     memory.
  5. Returns 404 cleanly for missing files.

Usage
~~~~~
Registered unconditionally in devbio/urls.py (replaces the DEBUG-only
``static()`` helper), so media serving works in both dev and production.

Production note
~~~~~~~~~~~~~~~
For high-traffic deployments, replace this view with a proper nginx
``location /media/ { alias /path/to/media/; }`` block and remove the
URL pattern from urls.py — that is always faster.  But for personal /
small-scale self-hosting this view is perfectly fine.
"""

import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden


def serve_media(request, path: str):
    """Stream a file from MEDIA_ROOT.  Safe against path-traversal attacks."""
    media_root = Path(settings.MEDIA_ROOT).resolve()

    # Build absolute path and resolve symlinks / ".." components
    requested = (media_root / path).resolve()

    # Security: reject anything that escapes MEDIA_ROOT
    try:
        requested.relative_to(media_root)
    except ValueError:
        return HttpResponseForbidden('Access denied.')

    if not requested.exists() or not requested.is_file():
        raise Http404(f'Media file not found: {path}')

    content_type, _ = mimetypes.guess_type(str(requested))
    content_type = content_type or 'application/octet-stream'

    return FileResponse(
        open(requested, 'rb'),
        content_type=content_type,
        as_attachment=False,
    )
