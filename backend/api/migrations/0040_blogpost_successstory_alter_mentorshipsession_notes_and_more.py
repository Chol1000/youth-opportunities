# Generated manually for blog models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20250704_0005'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField(default='')),
                ('excerpt', models.TextField(blank=True, default='')),
                ('featured_image', models.ImageField(blank=True, null=True, upload_to='blog_images/')),
                ('author', models.CharField(default='Youth Opportunities Team', max_length=100)),
                ('author_avatar', models.ImageField(blank=True, null=True, upload_to='author_avatars/')),
                ('category', models.CharField(default='General', max_length=50)),
                ('is_featured', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('read_time', models.CharField(default='5 min read', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SuccessStory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField(default='')),
                ('excerpt', models.TextField(blank=True, default='')),
                ('author_name', models.CharField(max_length=100)),
                ('author_email', models.EmailField(max_length=254)),
                ('author_location', models.CharField(blank=True, default='', max_length=100)),
                ('featured_image', models.ImageField(blank=True, null=True, upload_to='success_stories/')),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='mentorshipsession',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='mentorshipsession',
            name='request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.mentorrequest'),
        ),
    ]
