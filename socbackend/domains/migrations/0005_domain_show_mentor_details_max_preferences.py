# Generated migration for show_mentor_details and max_preferences fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0004_domain_project_deletion_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='show_mentor_details',
            field=models.BooleanField(default=True, help_text='Show mentor/co-mentor names and phone numbers to mentees'),
        ),
        migrations.AddField(
            model_name='domain',
            name='max_preferences',
            field=models.PositiveIntegerField(default=3, help_text='Maximum number of preferences mentees can fill'),
        ),
    ]
