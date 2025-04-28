
import csv
from django.core.management.base import BaseCommand
from projects.models import Project
import pandas as pd
from django.db import models 

class Command(BaseCommand):
    help = 'Import project data from a CSV file into the database, setting the ID starting from 1'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        try:
            # Load CSV data into a DataFrame
            df = pd.read_csv(csv_file)

            # Get the maximum current ID in the database, to continue from the last used ID
            max_id = Project.objects.aggregate(models.Max('id'))['id__max'] or 0
            new_id = max_id + 1

            # Iterate through the rows of the CSV
            for index, row in df.iterrows():
                # Check if the project already exists based on title and description
                if Project.objects.filter(title=row['Title'], description=row['Description']).exists():
                    print(f"Project '{row['Title']}' already exists")
                    continue

                # Create and save the new Project instance
                project = Project(
                    id=new_id,  # Set the manually incremented ID
                    title=row['Title'],
                    description=row['Description'],
                    checkpoints=row.get('Checkpoints', 'NA'),
                    timeline=row.get('Timeline', 'NA'),
                    mentor=row.get('Mentor', 'NA'),
                    co_mentor_info=row.get('Co-Mentor Info', 'NA'),
                    specific_category=row.get('Specific Category', 'NA'),
                    general_category=row.get('General Category', 'Others'),
                    mentee_max=row.get('Mentee Max', '0'),
                    prereuisites=row.get('Prerequisites', 'NA'),
                    banner_image_link=row.get('Banner Image Link', ''),
                    code=row.get('Code', '')
                )

                # Save the project to the database
                project.save()

                print(f"Project '{row['Title']}' imported successfully with ID {new_id}")

                # Increment the ID for the next project
                new_id += 1

            print("Done importing projects.")
        except FileNotFoundError:
            print(f"Error: File '{csv_file}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
