# Generated manually to add missing submitted_at field to CVReview

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_add_cvreview_additional_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='cvreview',
            name='submitted_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='cvreview',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
