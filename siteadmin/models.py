"""
siteadmin/models.py
-------------------
Models:
  PlanFeature       – A named, configurable feature (e.g. "profile_themes").
                      Admin creates these and assigns them to plans.
  PlanFeatureValue  – The value/limit of a feature for a specific plan
                      (e.g. plan=Pro, feature=max_links, value=50).
  SubscriptionPlan  – A subscription tier definition.
  Subscription      – Per-user plan assignment.
  SiteSettings      – Singleton for global webapp settings.
"""

from django.db import models
from django.conf import settings


# ── Feature catalogue ─────────────────────────────────────────────────────────

FEATURE_TYPE_BOOL    = 'bool'
FEATURE_TYPE_INT     = 'int'
FEATURE_TYPE_CHOICES = 'choices'

FEATURE_TYPE_OPTIONS = [
    (FEATURE_TYPE_BOOL,    'On / Off toggle'),
    (FEATURE_TYPE_INT,     'Numeric limit (0 = unlimited)'),
    (FEATURE_TYPE_CHOICES, 'Choice list (comma-separated)'),
]

# These slugs are referenced in code — do not rename them.
FEATURE_PROFILE_THEMES        = 'profile_themes'       # bool
FEATURE_CUSTOM_FONTS          = 'custom_fonts'          # bool
FEATURE_CUSTOM_LAYOUT         = 'custom_layout'         # bool
FEATURE_BACKGROUND_IMAGE      = 'background_image'      # bool
FEATURE_CUSTOM_COLORS         = 'custom_colors'         # bool
FEATURE_MAX_LINKS             = 'max_links'             # int (0=unlimited)
FEATURE_USERNAME_CHANGES      = 'username_changes_pm'   # int (0=unlimited, per month)
FEATURE_EXTRA_PROFILES        = 'extra_profiles'        # int (0=just the 1 default)
FEATURE_SEO_TAGS              = 'seo_tags'              # bool
FEATURE_ANALYTICS             = 'analytics'             # bool
FEATURE_REMOVE_BADGE          = 'remove_badge'          # bool
FEATURE_PRIORITY_LOADING      = 'priority_loading'      # bool


class PlanFeature(models.Model):
    """
    A named capability that can be toggled or limited per plan.
    Admin creates/edits these from the Subscription Plans section.
    """
    slug         = models.SlugField(max_length=60, unique=True)
    name         = models.CharField(max_length=100)
    description  = models.CharField(max_length=200, blank=True)
    feature_type = models.CharField(max_length=10,
                                    choices=FEATURE_TYPE_OPTIONS,
                                    default=FEATURE_TYPE_BOOL)
    # For CHOICES type: comma-separated allowed values
    choices_list = models.CharField(max_length=400, blank=True,
                                    help_text='Comma-separated values, e.g. minimal,glass,neon')
    # Default value used when a plan has no explicit PlanFeatureValue row
    default_value = models.CharField(max_length=100, default='false',
                                     help_text='false / true for bool; integer for int; choice slug for choices')
    order        = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'slug']

    def __str__(self):
        return self.name

    def cast(self, raw):
        """Return raw string value cast to the correct Python type."""
        if self.feature_type == FEATURE_TYPE_BOOL:
            return str(raw).lower() in ('true', '1', 'yes')
        if self.feature_type == FEATURE_TYPE_INT:
            try:
                return int(raw)
            except (ValueError, TypeError):
                return 0
        return str(raw)  # choices — return as string


class PlanFeatureValue(models.Model):
    """
    The value of a specific feature for a specific plan.
    If no row exists for a plan+feature combo, PlanFeature.default_value is used.
    """
    plan    = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE,
                                related_name='feature_values')
    feature = models.ForeignKey(PlanFeature, on_delete=models.CASCADE,
                                related_name='plan_values')
    value   = models.CharField(max_length=200, default='false')

    class Meta:
        unique_together = [('plan', 'feature')]

    def __str__(self):
        return f'{self.plan.name} / {self.feature.slug} = {self.value}'

    def cast(self):
        return self.feature.cast(self.value)


# ── Subscription Plan ─────────────────────────────────────────────────────────

class SubscriptionPlan(models.Model):
    slug         = models.SlugField(max_length=30, unique=True)
    name         = models.CharField(max_length=80)
    price        = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_label  = models.CharField(max_length=40, blank=True, default='/month')
    description  = models.CharField(max_length=160, blank=True)
    features     = models.TextField(blank=True,
                                    help_text='Marketing bullet points (one per line)')
    is_featured  = models.BooleanField(default=False)
    show_on_home = models.BooleanField(default=True)
    order        = models.PositiveSmallIntegerField(default=0)
    cta_label    = models.CharField(max_length=60, blank=True, default='Get started')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.name}'

    def features_list(self):
        return [l.strip() for l in self.features.splitlines() if l.strip()]

    def get_feature(self, slug, default=None):
        """Return the cast value for a feature slug on this plan."""
        try:
            pfv = self.feature_values.select_related('feature').get(feature__slug=slug)
            return pfv.cast()
        except PlanFeatureValue.DoesNotExist:
            pass
        try:
            pf = PlanFeature.objects.get(slug=slug)
            return pf.cast(pf.default_value)
        except PlanFeature.DoesNotExist:
            return default


# ── Per-user Subscription ─────────────────────────────────────────────────────

class Subscription(models.Model):
    user      = models.OneToOneField(settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE, related_name='subscription')
    plan_slug = models.CharField(max_length=30, default='free')
    plan      = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='subscriptions')
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notes     = models.TextField(blank=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.username} — {self.plan_slug}'

    def get_plan_display(self):
        return self.plan.name if self.plan else self.plan_slug.capitalize()

    def has_feature(self, slug):
        """Return True if this subscription's plan enables the feature."""
        if not self.is_active or not self.plan:
            return False
        val = self.plan.get_feature(slug)
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val != 0   # 0 = disabled for int features
        return bool(val)

    def feature_limit(self, slug):
        """Return the numeric limit for an int feature (0 = unlimited)."""
        if not self.is_active or not self.plan:
            return 0
        val = self.plan.get_feature(slug)
        try:
            return int(val) if val is not None else 0
        except (ValueError, TypeError):
            return 0


# ── Site Settings ─────────────────────────────────────────────────────────────

SITE_THEME_CHOICES = [
    ('dark',   'Dark (Default)'),
    ('light',  'Light'),
    ('ocean',  'Ocean Blue'),
    ('forest', 'Forest Green'),
    ('rose',   'Rose'),
]


class SiteSettings(models.Model):
    site_name       = models.CharField(max_length=80, default='CybFlows')
    tagline         = models.CharField(max_length=160, blank=True,
                                       default='Your link, your identity.')
    site_theme      = models.CharField(max_length=20, choices=SITE_THEME_CHOICES, default='dark')
    accent_color    = models.CharField(max_length=7, default='#ff4d00')
    allow_signup    = models.BooleanField(default=True)
    maintenance     = models.BooleanField(default=False)
    maintenance_msg = models.TextField(blank=True,
                                       default='We are performing scheduled maintenance. Back soon.')
    footer_text     = models.CharField(max_length=200, blank=True,
                                       default='Free & open-source link-in-bio for creators.')
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'

    def __str__(self):
        return f'Site Settings (theme: {self.site_theme})'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
