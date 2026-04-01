# Generated migration for adding project_creation_open and project_editing_open fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0002_domain_mentee_reg_open_domain_mentor_reg_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='project_creation_open',
            field=models.BooleanField(default=True, help_text='Allow mentors to create new projects'),
        ),
        migrations.AddField(
            model_name='domain',
            name='project_editing_open',
            field=models.BooleanField(default=True, help_text='Allow mentors to edit existing projects'),
        ),
    ]
