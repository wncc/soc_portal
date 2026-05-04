# Generated migration for additional general category choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_alter_ranklist_unique_together_mentee_domain_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='general_category',
            field=models.CharField(
                choices=[
                    ('Machine Learning', 'Machine Learning'),
                    ('Development', 'Development'),
                    ('Blockchain', 'Blockchain'),
                    ('Competitive Programming', 'Competitive Programming'),
                    ('Quant / Finance', 'Quant / Finance'),
                    ('Robotics / Hardware', 'Robotics / Hardware'),
                    ('Mathematics', 'Mathematics'),
                    ('Physics', 'Physics'),
                    ('Engineering', 'Engineering'),
                    ('Astronomy and Astrophysics, and Planetary Science', 'Astronomy and Astrophysics, and Planetary Science'),
                    ('Biology, Biotechnology and Biophysics', 'Biology, Biotechnology and Biophysics'),
                    ('Computer Science', 'Computer Science'),
                    ('Applied Science, Humanities, and Miscellaneous', 'Applied Science, Humanities, and Miscellaneous'),
                    ('Energy Science', 'Energy Science'),
                    ('Chemistry and Material Science', 'Chemistry and Material Science'),
                    ('Others', 'Others'),
                ],
                default='Others',
                max_length=255
            ),
        ),
    ]
