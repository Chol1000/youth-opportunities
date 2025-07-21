# Generated manually to add missing updated_at field to UserDocument

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_add_experience_skills_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocument',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
