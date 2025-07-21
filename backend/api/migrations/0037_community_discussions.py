# Generated manually for community discussions

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20250703_1913'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(choices=[('career-advice', 'Career Advice'), ('interview-tips', 'Interview Tips'), ('resume-help', 'Resume Help'), ('networking', 'Networking'), ('success-stories', 'Success Stories')], max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CommunityReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='api.communitydiscussion')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
