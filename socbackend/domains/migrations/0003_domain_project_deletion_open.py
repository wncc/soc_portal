# Generated migration for project_deletion_open field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0002_auto_previous'),  # Update this to your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='project_deletion_open',
            field=models.BooleanField(default=False, help_text='Allow mentors to delete their projects'),
        ),
    ]
