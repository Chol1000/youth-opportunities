# Fix mentorship session fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20250704_0018'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE api_mentorshipsession SET notes = '' WHERE notes IS NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "UPDATE api_mentorshipsession SET request_id = NULL WHERE request_id NOT IN (SELECT id FROM api_mentorrequest);",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
