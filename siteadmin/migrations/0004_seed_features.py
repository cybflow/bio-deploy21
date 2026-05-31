"""
0004_seed_features.py — Seeds the default feature catalogue and sets
values for the three default plans (Free, Pro, Enterprise).
"""
from django.db import migrations


FEATURES = [
    # slug, name, description, type, default, order
    ('profile_themes',      'Profile Themes',         'Access to premium profile themes',               'bool', 'false', 0),
    ('custom_fonts',        'Custom Fonts',           'Choose a custom font for your profile page',     'bool', 'false', 1),
    ('custom_layout',       'Custom Layout',          'Choose the layout style for your links',         'bool', 'false', 2),
    ('background_image',    'Background Image',       'Upload a background image for your profile',     'bool', 'false', 3),
    ('custom_colors',       'Custom Colors',          'Set custom accent, background, and text colours','bool', 'false', 4),
    ('max_links',           'Max Links',              'Maximum number of links (0 = unlimited)',         'int',  '5',     5),
    ('username_changes_pm', 'Username Changes / Month','How many times a user can change their username per month (0 = unlimited)', 'int', '1', 6),
    ('extra_profiles',      'Extra Profiles',         'Number of additional profile usernames (0 = none)','int', '0',   7),
    ('seo_tags',            'SEO Meta Tags',          'Adds Open Graph / Twitter Card meta tags',       'bool', 'false', 8),
    ('analytics',           'Click Analytics',        'Track click counts on links',                    'bool', 'false', 9),
    ('remove_badge',        'Remove AEiViON Badge',   'Hide the "Made with AEiViON" watermark',        'bool', 'false', 10),
    ('priority_loading',    'Priority Loading',       'Profile page served with priority cache headers','bool', 'false', 11),
]

# plan_slug → {feature_slug: value}
PLAN_VALUES = {
    'free': {
        'profile_themes':      'false',
        'custom_fonts':        'false',
        'custom_layout':       'false',
        'background_image':    'false',
        'custom_colors':       'false',
        'max_links':           '5',
        'username_changes_pm': '1',
        'extra_profiles':      '0',
        'seo_tags':            'false',
        'analytics':           'false',
        'remove_badge':        'false',
        'priority_loading':    'false',
    },
    'pro': {
        'profile_themes':      'true',
        'custom_fonts':        'true',
        'custom_layout':       'true',
        'background_image':    'true',
        'custom_colors':       'true',
        'max_links':           '0',
        'username_changes_pm': '5',
        'extra_profiles':      '2',
        'seo_tags':            'true',
        'analytics':           'true',
        'remove_badge':        'true',
        'priority_loading':    'false',
    },
    'enterprise': {
        'profile_themes':      'true',
        'custom_fonts':        'true',
        'custom_layout':       'true',
        'background_image':    'true',
        'custom_colors':       'true',
        'max_links':           '0',
        'username_changes_pm': '0',
        'extra_profiles':      '10',
        'seo_tags':            'true',
        'analytics':           'true',
        'remove_badge':        'true',
        'priority_loading':    'true',
    },
}


def seed(apps, schema_editor):
    PlanFeature       = apps.get_model('siteadmin', 'PlanFeature')
    PlanFeatureValue  = apps.get_model('siteadmin', 'PlanFeatureValue')
    SubscriptionPlan  = apps.get_model('siteadmin', 'SubscriptionPlan')

    feature_map = {}
    for slug, name, desc, ftype, default, order in FEATURES:
        pf, _ = PlanFeature.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': desc,
                      'feature_type': ftype, 'default_value': default, 'order': order},
        )
        feature_map[slug] = pf

    for plan_slug, values in PLAN_VALUES.items():
        try:
            plan = SubscriptionPlan.objects.get(slug=plan_slug)
        except SubscriptionPlan.DoesNotExist:
            continue
        for fslug, val in values.items():
            pf = feature_map.get(fslug)
            if pf:
                PlanFeatureValue.objects.update_or_create(
                    plan=plan, feature=pf,
                    defaults={'value': val},
                )


def unseed(apps, schema_editor):
    PlanFeature = apps.get_model("siteadmin", "PlanFeature")
    PlanFeature.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [('siteadmin', '0003_planfeature')]
    operations   = [migrations.RunPython(seed, reverse_code=unseed)]
