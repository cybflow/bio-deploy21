from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # SiteSettings singleton
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('site_name',       models.CharField(default='AEiViON', max_length=80)),
                ('tagline',         models.CharField(blank=True, default='Your link, your identity.', max_length=160)),
                ('site_theme',      models.CharField(choices=[('dark','Dark (Default)'),('light','Light'),('ocean','Ocean Blue'),('forest','Forest Green'),('rose','Rose')], default='dark', max_length=20)),
                ('accent_color',    models.CharField(default='#ff4d00', max_length=7)),
                ('allow_signup',    models.BooleanField(default=True)),
                ('maintenance',     models.BooleanField(default=False)),
                ('maintenance_msg', models.TextField(blank=True, default='We are performing scheduled maintenance. Back soon.')),
                ('footer_text',     models.CharField(blank=True, default='Free & open-source link-in-bio for creators.', max_length=200)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Site Settings'},
        ),
        # SubscriptionPlan definitions
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('slug',        models.SlugField(max_length=30, unique=True)),
                ('name',        models.CharField(max_length=80)),
                ('price',       models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('price_label', models.CharField(blank=True, default='/month', max_length=40)),
                ('description', models.CharField(blank=True, max_length=160)),
                ('features',    models.TextField(blank=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('show_on_home',models.BooleanField(default=True)),
                ('order',       models.PositiveSmallIntegerField(default=0)),
                ('cta_label',   models.CharField(blank=True, default='Get started', max_length=60)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('updated_at',  models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['order', 'id']},
        ),
        # Per-user subscription assignment
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('plan_slug',  models.CharField(default='free', max_length=30)),
                ('is_active',  models.BooleanField(default=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('notes',      models.TextField(blank=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subscription',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('plan', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='subscriptions',
                    to='siteadmin.subscriptionplan',
                )),
            ],
            options={'ordering': ['user__username']},
        ),
    ]
