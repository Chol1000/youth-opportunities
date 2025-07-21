# Generated manually to add missing foreign key

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_community_discussions'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityreply',
            name='discussion',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='api.communitydiscussion'),
            preserve_default=False,
        ),
    ]
