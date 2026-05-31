from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='theme',
            field=models.CharField(
                choices=[
                    ('default',   'Default (Dark Glass)'),
                    ('clay',      'Clay Morphism'),
                    ('minimal',   'Minimalism'),
                    ('brutalist', 'Neo Brutalism'),
                ],
                default='default',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='color_primary',
            field=models.CharField(default='#ff4d00', max_length=7),
        ),
        migrations.AddField(
            model_name='user',
            name='color_bg',
            field=models.CharField(default='#050505', max_length=7),
        ),
        migrations.AddField(
            model_name='user',
            name='color_text',
            field=models.CharField(default='#f0f0f0', max_length=7),
        ),
        migrations.AddField(
            model_name='user',
            name='bg_image',
            field=models.ImageField(blank=True, upload_to='bg_images/'),
        ),
    ]
