# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_add_opportunity_missing_fields'),
    ]

    operations = [
        # Update opportunity types
        migrations.AlterField(
            model_name='opportunity',
            name='opportunity_type',
            field=models.CharField(choices=[
                ('scholarship', 'Scholarship'),
                ('job', 'Job'),
                ('internship', 'Internship'),
                ('fellowship', 'Fellowship'),
                ('grant', 'Grant'),
                ('competition', 'Competition'),
                ('conference', 'Conference'),
                ('workshop', 'Workshop'),
                ('training', 'Training'),
                ('service', 'Service'),
                ('blog', 'Blog'),
                ('announcement', 'Announcement'),
                ('miscellaneous', 'Miscellaneous'),
            ], max_length=20),
        ),
        # Update existing records with old types
        migrations.RunSQL(
            "UPDATE api_opportunity SET opportunity_type = 'miscellaneous' WHERE opportunity_type IN ('course', 'volunteer', 'exchange', 'other');",
            reverse_sql="UPDATE api_opportunity SET opportunity_type = 'other' WHERE opportunity_type = 'miscellaneous';"
        ),
    ]
