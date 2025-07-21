# Generated manually to add missing skills field to Experience

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_add_final_missing_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='skills',
            field=models.TextField(blank=True),
        ),
    ]
