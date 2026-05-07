# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0005_domain_show_mentor_details_max_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='mentor_portal_access',
            field=models.BooleanField(default=True, help_text='Allow mentors to access mentor portal and view their projects'),
        ),
    ]
