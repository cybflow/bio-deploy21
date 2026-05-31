"""
Django settings for devbio — production-ready.

Key behaviours
--------------
* DEBUG is driven by the DEBUG environment variable (default True for dev).
* When DEBUG=False, WhiteNoise serves static files.
* Media files (avatars, bg images) are served via a dedicated Django URL
  pattern that works in BOTH debug and production without needing a
  separate web-server rewrite rule.  The view is protected behind a
  lightweight streaming file-serve view defined in devbio/media_serve.py.
* A DATA_DIR fallback keeps SQLite WAL journals on an ext4 filesystem
  when running inside Termux on Android.
"""

from pathlib import Path
import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Termux / Android: keep DB + media on ext4, not FAT
_HOME       = Path(os.environ.get('HOME', str(BASE_DIR)))
_IS_TERMUX  = 'com.termux' in str(_HOME)
DATA_DIR    = _HOME / '.devbio' if _IS_TERMUX else BASE_DIR

# Ensure media and static sub-directories exist at startup
(DATA_DIR / 'media' / 'avatars').mkdir(parents=True, exist_ok=True)
(DATA_DIR / 'media' / 'bg_images').mkdir(parents=True, exist_ok=True)
(DATA_DIR / 'staticfiles').mkdir(parents=True, exist_ok=True)

# ── Core security ─────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-pu(a^l02+_-t*xm5w=pue(!_b#o0tjq8l^n851$v-&%p4^6iy9',
)

DEBUG = os.environ.get('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')

# Allow * in dev; in production set ALLOWED_HOSTS env var to a comma-separated
# list of real host names, e.g. "example.com,www.example.com"
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    _raw = os.environ.get('ALLOWED_HOSTS', 'getbio.cybflows.com,localhost')
    ALLOWED_HOSTS = [h.strip() for h in _raw.split(',') if h.strip()]

# ── Application definition ────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # project apps
    'accounts',
    'links',
    'dashboard',
    'public',
    'siteadmin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must come immediately after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # MaintenanceMiddleware must come AFTER AuthenticationMiddleware
    # so that request.user is available for the is_staff bypass check.
    'devbio.middleware.MaintenanceMiddleware',
]
CSRF_TRUSTED_ORIGINS = [
    "https://*.cybflows.com",
]

ROOT_URLCONF = 'devbio.urls'


CSRF_TRUSTED_ORIGINS = [
    "https://*.cybflows.com",
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'devbio.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'devbio.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL     = 'accounts.User'
DEFAULT_AUTO_FIELD  = 'django.db.models.BigAutoField'

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ── Static files ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'

# IMPORTANT — Termux / Android:
# collectstatic calls fcntl.flock() when writing files.  The FAT-based FUSE
# filesystem at /storage/emulated/0/ does NOT implement flock, which causes:
#   OSError: [Errno 38] Function not implemented
#
# The fix is to keep STATIC_ROOT on the same ext4 partition as DATA_DIR
# (/data/data/com.termux/files/home/.devbio/staticfiles) where flock works.
# On a normal Linux/macOS/Windows host this resolves to BASE_DIR/staticfiles
# as expected — nothing changes for non-Termux deployments.
STATIC_ROOT = DATA_DIR / 'staticfiles'

# WhiteNoise compressed static file storage (works with DEBUG=False).
# Uses ManifestStaticFilesStorage on Termux to avoid the CompressedManifest
# variant's gzip step, which also triggers flock on some Android kernels.
if _IS_TERMUX:
    STATICFILES_STORAGE = 'whitenoise.storage.ManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Media files ───────────────────────────────────────────────────────────────
# IMPORTANT: Django's built-in static() helper in urls.py only works when
# DEBUG=True.  For production (DEBUG=False) we register a dedicated
# media-serving URL in devbio/urls.py that calls our custom streaming
# view (devbio/media_serve.py).  That view reads files from MEDIA_ROOT
# and streams them with the correct Content-Type — no web-server config
# required, works with gunicorn out of the box.
MEDIA_URL  = '/media/'
MEDIA_ROOT = DATA_DIR / 'media'

# ── Session ───────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE      = 1_209_600   # 2 weeks
SESSION_COOKIE_HTTPONLY = True

# ── Production-only hardening ─────────────────────────────────────────────────
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER   = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS             = 'DENY'
    # Uncomment when you have HTTPS:
    # SECURE_SSL_REDIRECT        = True
    # SESSION_COOKIE_SECURE      = True
    # CSRF_COOKIE_SECURE         = True
