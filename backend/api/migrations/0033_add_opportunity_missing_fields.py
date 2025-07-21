# Generated manually to add missing Opportunity fields for frontend

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_add_cvreview_submitted_at'),
    ]

    operations = [
        # Update opportunity types to include missing ones
        migrations.AlterField(
            model_name='opportunity',
            name='opportunity_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('scholarship', 'Scholarship'),
                    ('job', 'Job'),
                    ('internship', 'Internship'),
                    ('fellowship', 'Fellowship'),
                    ('grant', 'Grant'),
                    ('competition', 'Competition'),
                    ('conference', 'Conference'),
                    ('workshop', 'Workshop'),
                    ('training', 'Training'),
                    ('announcement', 'Announcement'),
                    ('miscellaneous', 'Miscellaneous'),
                    ('course', 'Course'),
                    ('volunteer', 'Volunteer'),
                    ('exchange', 'Exchange Program'),
                    ('other', 'Other'),
                ]
            ),
        ),
        # Add missing tracking fields
        migrations.AddField(
            model_name='opportunity',
            name='views_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='clicks_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='shares_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
