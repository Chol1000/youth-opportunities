# Generated migration for mentorship updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_communitypost_shared_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorrequest',
            name='preferred_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mentorrequest',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mentorshipsession',
            name='google_meet_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mentorshipsession',
            name='duration',
            field=models.PositiveIntegerField(default=60, help_text='Duration in minutes'),
        ),
        migrations.AlterUniqueTogether(
            name='mentorrequest',
            unique_together=set(),
        ),
    ]
