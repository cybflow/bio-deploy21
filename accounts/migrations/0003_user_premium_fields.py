from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_theme_fields'),
    ]

    operations = [
        migrations.AddField(model_name='user', name='profile_font',
            field=models.CharField(choices=[('dm_sans','DM Sans (Default)'),('inter','Inter'),('poppins','Poppins'),('space_grotesk','Space Grotesk'),('playfair','Playfair Display'),('roboto_mono','Roboto Mono')], default='dm_sans', max_length=30)),
        migrations.AddField(model_name='user', name='profile_layout',
            field=models.CharField(choices=[('centered','Centered (Default)'),('left_align','Left Aligned'),('card_stack','Card Stack'),('grid','Grid')], default='centered', max_length=30)),
        migrations.AddField(model_name='user', name='username_changed_at',
            field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='user', name='username_changes_month',
            field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name='user', name='username_change_month',
            field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name='user', name='username_change_year',
            field=models.PositiveSmallIntegerField(default=0)),
    ]
