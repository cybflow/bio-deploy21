from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('siteadmin', '0002_seed_default_plans'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanFeature',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('slug',          models.SlugField(max_length=60, unique=True)),
                ('name',          models.CharField(max_length=100)),
                ('description',   models.CharField(blank=True, max_length=200)),
                ('feature_type',  models.CharField(choices=[('bool','On / Off toggle'),('int','Numeric limit (0 = unlimited)'),('choices','Choice list (comma-separated)')], default='bool', max_length=10)),
                ('choices_list',  models.CharField(blank=True, max_length=400)),
                ('default_value', models.CharField(default='false', max_length=100)),
                ('order',         models.PositiveSmallIntegerField(default=0)),
            ],
            options={'ordering': ['order', 'slug']},
        ),
        migrations.CreateModel(
            name='PlanFeatureValue',
            fields=[
                ('id',      models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('value',   models.CharField(default='false', max_length=200)),
                ('plan',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feature_values', to='siteadmin.subscriptionplan')),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_values', to='siteadmin.planfeature')),
            ],
            options={'unique_together': {('plan', 'feature')}},
        ),
    ]
