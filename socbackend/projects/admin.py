# from django.contrib import admin
# # from django.contrib import admin
# from .models import Project, Mentee,Mentor, MenteePreference, MenteeWishlist ,RankList


# # class MentorInline(admin.TabularInline):
# #     model = MentorRequest
# #     max_num = 4
# #     extra = 1


# # class ProjectAdmin(admin.ModelAdmin):
# #     model = Project
# #     inlines = [MentorInline]

# class MenteeAdmin(admin.ModelAdmin):
#     list_per_page = 1000  
# class MentorAdmin(admin.ModelAdmin):
#     list_per_page = 1000  
# class RankListAdmin(admin.ModelAdmin):
#     list_per_page = 1000  

# # Register your models here.
# # admin.site.register(Season)
# # admin.site.register(Project, ProjectAdmin)
# # admin.site.register(Mentor)
# admin.site.register(Project)    
# admin.site.register(Mentor, MentorAdmin)
# admin.site.register(Mentee, MenteeAdmin)
# admin.site.register(RankList, RankListAdmin)
# # admin.site.register(ProjectCategory)
# admin.site.register(MenteePreference)
# admin.site.register(MenteeWishlist)


from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Project, Mentee, Mentor, MenteePreference, MenteeWishlist, RankList
from accounts.models import UserProfile,CustomUser

# Admin class for Mentee
class MenteeAdmin(admin.ModelAdmin):
    list_per_page = 1000  

# Admin class for Mentor
class MentorAdmin(admin.ModelAdmin):
    list_per_page = 1000  

# Admin class for RankList
class RankListAdmin(admin.ModelAdmin):
    list_per_page = 1000  

    # Export selected mentees to CSV action
    @admin.action(description="Export mentees selected for projects to CSV")
    def export_selected_mentees_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="selected_mentees.csv"'
        writer = csv.writer(response)

        # Write header row
        writer.writerow(['Project Title', 'Project Id', 'Mentor Roll Number','Mentor Name' ,'Mentee Roll Number','Mentee Name' ,'Rank Given', 'Mentee Preference'])

        # Initialize a set to keep track of mentees that are already assigned to a project
        assigned_mentees = set()

        # Process each selected RankList entry (projects)
        for ranklist in queryset:
            project = ranklist.project
            max_mentees = int(project.mentee_max)  # Maximum mentees for this project

            # Get all ranklist entries for this project and sort by rank and preference
            rank_entries = RankList.objects.filter(project=project).order_by('rank', 'preference')

            selected_mentees = []
            selected_ids = set()

            # Select mentees based on rank and preference
            for rank in rank_entries:
                if len(selected_mentees) >= max_mentees:  # If we've selected enough mentees, stop
                    break
                if rank.mentee.id not in assigned_mentees:  # Ensure mentee is not selected more than once
                    selected_mentees.append(rank)
                    selected_ids.add(rank.mentee.id)
                    assigned_mentees.add(rank.mentee.id)  # Mark this mentee as assigned

            # Write the selected mentees to CSV
            for selected in selected_mentees:
                writer.writerow([
                    selected.project.title,               # Project Title
                    selected.project.id,              # Project Code
                    selected.mentor.user.roll_number,     # Mentor Roll Number
                    selected.mentor.user.name,
                    selected.mentee.user.roll_number,     # Mentee Roll Number
                    selected.mentee.user.name,
                    selected.rank,                        # Rank Given
                    selected.preference                   # Mentee Preference
                ])

        return response

    actions = [export_selected_mentees_to_csv]

# class MentorAdmin(admin.ModelAdmin):
#     list_display = ('get_name', 'get_roll_number', 'list_projects')  # Access fields via related user model
#     search_fields = ('user__name',)  # Add search functionality by mentor's name (through user)

#     # Custom method to get mentor's name
#     def get_name(self, obj):
#         return obj.user.name  # Access the 'name' field from the related User model
#     get_name.short_description = 'Name'  # Display label for 'Name' column
    
#     # Custom method to get mentor's roll number
#     def get_roll_number(self, obj):
#         return obj.user.roll_number  # Access the 'roll_number' field from the related User model
#     get_roll_number.short_description = 'Roll Number'  # Display label for 'Roll Number' column

#     # Custom method to list the projects associated with the mentor
#     def list_projects(self, obj):
#         # Filter projects associated with this mentor
#         projects = obj.projects.all()
#         # Return a comma-separated string of project titles
#         return ', '.join([project.title for project in projects]) if projects else 'No projects'
#     list_projects.short_description = 'Projects'  # Custom label for the 'Projects' column

#     # Filter mentors who have at least one project
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.filter(projects__isnull=False).distinct()  # Filter mentors who have projects registered


from django.db import models  # make sure this is imported

class MentorAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_roll_number', 'list_projects', 'get_project_count')
    search_fields = ('user__name',)

    # Show mentor's name
    def get_name(self, obj):
        return obj.user.name
    get_name.short_description = 'Name'

    # Show mentor's roll number
    def get_roll_number(self, obj):
        return obj.user.roll_number
    get_roll_number.short_description = 'Roll Number'

    # Show projects linked to the mentor
    def list_projects(self, obj):
        projects = obj.projects.all()
        return ', '.join([project.title for project in projects]) if projects else 'No projects'
    list_projects.short_description = 'Projects'

    # Show number of projects
    def get_project_count(self, obj):
        return obj.project_count
    get_project_count.admin_order_field = 'project_count'  # This tells Django this column is sortable
    get_project_count.short_description = 'Number of Projects'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(project_count=models.Count('projects')).order_by('-project_count')  # <-- order by annotated field
        return queryset


admin.site.register(Mentor, MentorAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(RankList, RankListAdmin)
admin.site.register(MenteePreference)
admin.site.register(MenteeWishlist)

import re

class ProjectAdmin(admin.ModelAdmin):
    list_per_page = 1000

    # List display with custom fields
    list_display = ('title', 'get_mentor_names', 'get_mentor_roll_numbers', 'get_co_mentor_names', 'get_co_mentor_roll_numbers', 'general_category', 'specific_category')  

    # Custom method to get mentor names
    def get_mentor_names(self, obj):
        mentor_names = []
        try:
            # Check if the 'mentor' field is set to "NA" or empty
            if obj.mentor == "NA" or not obj.mentor:
                # If mentor is "NA", get all mentors associated with the project
                mentors = Mentor.objects.filter(projects=obj)
            else:
                # If a valid mentor is assigned, fetch by name
                mentors = Mentor.objects.filter(user__name=obj.mentor)
            
            for mentor in mentors:
                if obj in mentor.projects.all():
                    mentor_names.append(mentor.user.name)
            return ', '.join(mentor_names) if mentor_names else 'No mentor'
        except Mentor.DoesNotExist:
            return 'No mentor'  # If no mentor found

    get_mentor_names.short_description = 'Mentors'  

    # Custom method to get mentor roll numbers
    def get_mentor_roll_numbers(self, obj):
        mentor_roll_numbers = []
        try:
            # Check if the 'mentor' field is set to "NA" or empty
            if obj.mentor == "NA" or not obj.mentor:
                # If mentor is "NA", get all mentors associated with the project
                mentors = Mentor.objects.filter(projects=obj)
            else:
                # If a valid mentor is assigned, fetch by name
                mentors = Mentor.objects.filter(user__name=obj.mentor)
            
            for mentor in mentors:
                if obj in mentor.projects.all():
                    mentor_roll_numbers.append(mentor.user.roll_number)
            return ', '.join(mentor_roll_numbers) if mentor_roll_numbers else 'No roll number'
        except Mentor.DoesNotExist:
            return 'No roll number'
        
    get_mentor_roll_numbers.short_description = 'Mentor Roll Numbers'  

    # Custom method to get co-mentor names
    def get_co_mentor_names(self, obj):
        co_mentor_names = []
        try:
            if obj.co_mentor_info:
                matches = re.findall(r'([A-Za-z\s]+)\s\((\w+)\)', obj.co_mentor_info)
                for match in matches:
                    name, _ = match
                    co_mentor_names.append(name)
                    # Check if the co-mentor is already a mentor of the project
                    co_mentor = Mentor.objects.filter(user__name=name).first()
                    if co_mentor and obj not in co_mentor.projects.all():
                        # If co-mentor is not a mentor for this project, add them as a mentor
                        co_mentor.projects.add(obj)
            return ', '.join(co_mentor_names) if co_mentor_names else 'No co-mentor'
        except Exception:
            return 'Error processing co-mentor info'

    get_co_mentor_names.short_description = 'Co-Mentors'  

    # Custom method to get co-mentor roll numbers
    def get_co_mentor_roll_numbers(self, obj):
        co_mentor_roll_numbers = []
        try:
            if obj.co_mentor_info:
                matches = re.findall(r'([A-Za-z\s]+)\s\((\w+)\)', obj.co_mentor_info)
                for _, roll_number in matches:
                    co_mentor_roll_numbers.append(roll_number)
            return ', '.join(co_mentor_roll_numbers) if co_mentor_roll_numbers else 'No co-mentors'
        except Exception:
            return 'Error processing co-mentor info'

    get_co_mentor_roll_numbers.short_description = 'Co-Mentor Roll Numbers' 

    # Export selected projects to CSV action
    @admin.action(description="Export selected projects to CSV")
    def export_projects_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'

        writer = csv.writer(response)
        writer.writerow([ 
            'Title', 'General Category', 'Specific Category', 'Mentee Max',
            'Mentor Names', 'Mentor Roll Numbers', 'Co-Mentor Names', 'Co-Mentor Roll Numbers', 
            'Co-Mentor Info', 'Weekly Meets', 'Description', 'Timeline', 'Checkpoints', 'Prerequisites', 
            'Banner Image Link', 'Code'
        ])

        for project in queryset:
            # Get all mentors and co-mentors associated with this project
            mentor_names = self.get_mentor_names(project)
            mentor_roll_numbers = self.get_mentor_roll_numbers(project)
            co_mentor_names = self.get_co_mentor_names(project)
            co_mentor_roll_numbers = self.get_co_mentor_roll_numbers(project)

            writer.writerow([ 
                project.title,
                project.general_category,
                project.specific_category,
                project.mentee_max,
                mentor_names,  # Comma-separated mentor names
                mentor_roll_numbers,  # Comma-separated mentor roll numbers
                co_mentor_names,  # Comma-separated co-mentor names
                co_mentor_roll_numbers,  # Comma-separated co-mentor roll numbers
                project.co_mentor_info,
                project.weekly_meets,
                project.description,
                project.timeline,
                project.checkpoints,
                project.prereuisites,
                project.banner_image_link,
                project.code
            ])

        return response

    actions = [export_projects_csv]
    
    @admin.action(description="Add co-mentor as mentor if not already")
    def add_co_mentor_as_mentor(self, request, queryset):
        for project in queryset:
            if project.co_mentor_info:
                matches = re.findall(r'([A-Za-z\s]+)\s\((\w+)\)', project.co_mentor_info)
                for match in matches:
                    name, roll_number = match
                    roll_number = roll_number.strip().lower()  # Normalize roll number

                    # Check if the co-mentor exists as a CustomUser with role 'mentor'
                    user = CustomUser.objects.filter(username=roll_number, role='mentor').first()

                    if user:
                        try:
                            # Check if the user has a corresponding UserProfile and that profile is a mentor
                            user_profile = UserProfile.objects.get(user=user, role='mentor')

                            # Check if the user is already a mentor for any project
                            mentor = Mentor.objects.get(user=user_profile)

                            # If the mentor is not already linked to this project, add them
                            if project not in mentor.projects.all():
                                mentor.projects.add(project)
                                self.message_user(request, f'Co-mentor {name} with roll number {roll_number} added as mentor for project {project.title}')
                            else:
                                self.message_user(request, f'Co-mentor {name} with roll number {roll_number} is already a mentor for this project.')

                        except UserProfile.DoesNotExist:
                            self.message_user(request, f'Mentor profile for roll number {roll_number} does not exist or role is incorrect.')
                        except Mentor.DoesNotExist:
                            self.message_user(request, f'Mentor object for {name} ({roll_number}) not found.')
                    else:
                        self.message_user(request, f'No mentor user found with roll number {roll_number}.')

        self.message_user(request, "Co-mentor check complete.")
        return None

    actions = [export_projects_csv,add_co_mentor_as_mentor]

# Register the ProjectAdmin with the Django admin panel
admin.site.register(Project, ProjectAdmin)
