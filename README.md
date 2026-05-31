# AEiViON — Link-in-bio webapp

A full-featured Django link-in-bio platform with a custom admin panel,
subscription plan management, and four profile themes.

---

## Quick start (Termux / Android)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply all database migrations  ← REQUIRED on every fresh install
python manage.py migrate

# 3. Start the development server
python manage.py runserver
```

`migrate` creates all tables and seeds three default subscription plans
(Free, Pro, Enterprise) automatically — no manual steps required.

---

## Create your admin account

```bash
python manage.py createsuperuser
```

Then visit `http://127.0.0.1:8000/siteadmin/` and log in.

To promote an existing account:

```bash
python manage.py shell -c "
from accounts.models import User
User.objects.filter(username='YOUR_USERNAME').update(is_staff=True, is_superuser=True)
"
```

---

## Production deployment

```bash
# Collect static files (Termux: files are written to ~/.devbio/staticfiles)
DEBUG=False python manage.py collectstatic --noinput

# Start gunicorn
DEBUG=False \
SECRET_KEY=your-secret-key \
ALLOWED_HOSTS=yourdomain.com \
gunicorn devbio.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## URL map

| URL | Description |
|-----|-------------|
| `/` | Public home page with pricing |
| `/@username` | Public profile page |
| `/dashboard/` | User dashboard |
| `/siteadmin/` | Custom admin panel (staff only) |
| `/admin/` | Django built-in admin |
| `/login/` `/signup/` `/logout/` | Auth |

---

## Admin panel features

- **Dashboard** — user count, link count, plan distribution, site status
- **Users** — search, filter by plan, edit username/email/password, toggle active, delete
- **Subscription Plans** — create/edit/delete plans, toggle home-page visibility, live preview
- **Site Settings** — site name, theme, accent colour, maintenance mode, signup toggle

---

## Notes

- On **Termux / Android** all data (database, media, static files) is stored in
  `~/.devbio/` on the ext4 partition to avoid `fcntl.flock` errors on the
  FAT-based `/storage/emulated/0/` filesystem.
- The `SECRET_KEY` in `settings.py` is for development only. Always set a
  strong key via the `SECRET_KEY` environment variable in production.
# bio-deploy
# bio-deploy21
# bio-deploy21
