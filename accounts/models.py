from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


THEME_CHOICES = [
    ('default',   'Default (Dark Glass)'),
    ('clay',      'Clay Morphism'),
    ('minimal',   'Minimalism'),
    ('brutalist', 'Neo Brutalism'),
]

FONT_CHOICES = [
    ('dm_sans',    'DM Sans (Default)'),
    ('inter',      'Inter'),
    ('poppins',    'Poppins'),
    ('space_grotesk', 'Space Grotesk'),
    ('playfair',   'Playfair Display'),
    ('roboto_mono','Roboto Mono'),
]

LAYOUT_CHOICES = [
    ('centered',  'Centered (Default)'),
    ('left_align','Left Aligned'),
    ('card_stack','Card Stack'),
    ('grid',      'Grid'),
]


class User(AbstractUser):
    name    = models.CharField(max_length=120, blank=True)
    bio     = models.TextField(blank=True)
    avatar  = models.ImageField(upload_to='avatars/', blank=True)

    github  = models.URLField(blank=True)
    website = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    # Profile theme
    theme         = models.CharField(max_length=20, choices=THEME_CHOICES, default='default')
    color_primary = models.CharField(max_length=7, default='#ff4d00')
    color_bg      = models.CharField(max_length=7, default='#050505')
    color_text    = models.CharField(max_length=7, default='#f0f0f0')
    bg_image      = models.ImageField(upload_to='bg_images/', blank=True)

    # Premium customisation fields (gated by subscription)
    profile_font   = models.CharField(max_length=30, choices=FONT_CHOICES, default='dm_sans')
    profile_layout = models.CharField(max_length=30, choices=LAYOUT_CHOICES, default='centered')

    # Username change tracking (per-month limit)
    username_changed_at    = models.DateTimeField(null=True, blank=True)
    username_changes_month = models.PositiveSmallIntegerField(default=0)
    username_change_month  = models.PositiveSmallIntegerField(default=0)  # stores month number
    username_change_year   = models.PositiveSmallIntegerField(default=0)  # stores year number

    def profile_url(self):
        return f'/@{self.username}'

    # ── Subscription helpers ──────────────────────────────────────────────────

    def _get_sub(self):
        """Return the Subscription object or None."""
        try:
            return self.subscription
        except Exception:
            return None

    def has_feature(self, slug):
        """Return True if the user's active plan enables this feature."""
        sub = self._get_sub()
        if sub:
            return sub.has_feature(slug)
        return False

    def feature_limit(self, slug):
        """Return numeric limit for the feature (0 = unlimited)."""
        sub = self._get_sub()
        if sub:
            return sub.feature_limit(slug)
        return 0

    # ── Username change quota ─────────────────────────────────────────────────

    def username_changes_this_month(self):
        """Return number of username changes made in the current calendar month."""
        now = timezone.now()
        if (self.username_change_month == now.month and
                self.username_change_year == now.year):
            return self.username_changes_month
        return 0

    def can_change_username(self):
        """
        Returns (allowed: bool, reason: str).
        feature_limit() returns 0 to mean "unlimited" for int-type features.
        When the plan has username_changes_pm = 0, the user gets unlimited changes.
        When there is no subscription or the feature row is absent, default to 1/month.
        """
        from siteadmin.models import FEATURE_USERNAME_CHANGES
        sub = self._get_sub()

        if not sub or not sub.is_active or not sub.plan:
            # No active plan — conservative default of 1 change per month
            limit = 1
        else:
            raw = sub.plan.get_feature(FEATURE_USERNAME_CHANGES)
            if raw is None:
                # Feature not defined on this plan — conservative default
                limit = 1
            else:
                limit = int(raw)  # 0 means unlimited

        # 0 = unlimited → always allow
        if limit == 0:
            return True, ''

        used = self.username_changes_this_month()
        if used >= limit:
            return False, (
                f'You have used {used} of your {limit} allowed username '
                f'change{"s" if limit != 1 else ""} this month. '
                'Upgrade to a higher plan for more changes or unlimited.'
            )
        return True, ''

    def record_username_change(self):
        """Increment the monthly username change counter."""
        now = timezone.now()
        if (self.username_change_month == now.month and
                self.username_change_year == now.year):
            self.username_changes_month += 1
        else:
            self.username_changes_month = 1
            self.username_change_month  = now.month
            self.username_change_year   = now.year
        self.username_changed_at = now
        self.save(update_fields=[
            'username_changes_month', 'username_change_month',
            'username_change_year', 'username_changed_at',
        ])
