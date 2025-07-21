# Generated migration for user profile enhancements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_communitypost_shared_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_views',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='mentor_rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
    ]
