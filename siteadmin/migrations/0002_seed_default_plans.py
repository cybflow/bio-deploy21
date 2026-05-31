"""
siteadmin/migrations/0002_seed_default_plans.py
------------------------------------------------
Data migration: seeds the three default subscription plans (Free, Pro,
Enterprise) immediately after the tables are created.

This means the home-page pricing section is populated right after
``python manage.py migrate`` with no manual shell steps required.
The migration is safe to re-run — get_or_create ensures it is idempotent.
"""

from django.db import migrations


FREE_FEATURES = (
    "Unlimited links\n"
    "Custom bio & avatar\n"
    "Public profile page\n"
    "Social link icons\n"
    "Mobile optimised"
)

PRO_FEATURES = (
    "Everything in Free\n"
    "4 profile themes\n"
    "Custom accent colour\n"
    "Background image\n"
    "Click analytics\n"
    "SEO meta tags"
)

ENTERPRISE_FEATURES = (
    "Everything in Pro\n"
    "Custom domain support\n"
    "Priority page loading\n"
    "Remove AEiViON badge\n"
    "Dedicated support\n"
    "SLA uptime guarantee"
)


def seed_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('siteadmin', 'SubscriptionPlan')

    SubscriptionPlan.objects.get_or_create(
        slug='free',
        defaults={
            'name':         'Free',
            'price':        '0.00',
            'price_label':  '/month',
            'description':  'Everything you need to get started.',
            'features':     FREE_FEATURES,
            'is_featured':  False,
            'show_on_home': True,
            'order':        0,
            'cta_label':    'Sign up free',
        },
    )

    SubscriptionPlan.objects.get_or_create(
        slug='pro',
        defaults={
            'name':         'Pro',
            'price':        '0.00',
            'price_label':  '/month · always free',
            'description':  'Open-source means Pro features are free.',
            'features':     PRO_FEATURES,
            'is_featured':  True,
            'show_on_home': True,
            'order':        1,
            'cta_label':    'Get started free',
        },
    )

    SubscriptionPlan.objects.get_or_create(
        slug='enterprise',
        defaults={
            'name':         'Enterprise',
            'price':        '0.00',
            'price_label':  'self-hosted',
            'description':  'Full control on your own infrastructure.',
            'features':     ENTERPRISE_FEATURES,
            'is_featured':  False,
            'show_on_home': True,
            'order':        2,
            'cta_label':    'View on GitHub',
        },
    )


def remove_plans(apps, schema_editor):
    """Reverse migration — removes only the seeded default plans."""
    SubscriptionPlan = apps.get_model('siteadmin', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(slug__in=['free', 'pro', 'enterprise']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('siteadmin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_plans, reverse_code=remove_plans),
    ]
