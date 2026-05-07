# Generated migration for adding mentee_portal_access field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0006_domain_mentor_portal_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='mentee_portal_access',
            field=models.BooleanField(default=True, help_text='Allow mentees to access mentee portal (projects, wishlist, preferences)'),
        ),
    ]
