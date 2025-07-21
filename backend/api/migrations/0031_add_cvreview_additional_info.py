# Generated manually to add missing additional_info field to CVReview

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_add_userdocument_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='cvreview',
            name='additional_info',
            field=models.TextField(blank=True),
        ),
    ]
