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

import csv
import io
import zipfile
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Project, Mentee, Mentor, MenteePreference, MenteeWishlist, RankList
from accounts.models import UserProfile,CustomUser

# Admin class for Mentee
class MenteeAdmin(admin.ModelAdmin):
    list_per_page = 1000

    # Adding search functionality by fields like 'name' and 'roll_number'
    search_fields = ('user__name', 'user__roll_number')

    # Optional: Custom fields can be added to list display for better admin UI
    list_display = ('get_name', 'get_roll_number')  # Example

    # Custom method to get the mentee's name
    def get_name(self, obj):
        return obj.user.name
    get_name.short_description = 'Mentee Name'

    # Custom method to get the mentee's roll number
    def get_roll_number(self, obj):
        return obj.user.roll_number
    get_roll_number.short_description = 'Mentee Roll Number'


# Admin class for Mentor
class MentorAdmin(admin.ModelAdmin):
    list_per_page = 1000  
    
    
    from django.contrib import admin
from django.http import HttpResponse
import csv, io, zipfile
from collections import defaultdict
from statistics import mean

from .models import RankList, Mentee

class RankListAdmin(admin.ModelAdmin):
    list_per_page = 1000

    @admin.action(description="combine karo")
    def export_selected_mentees_to_csv(self, request, queryset):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            selected_buffer = io.StringIO()
            selected_writer = csv.writer(selected_buffer)

            log_buffer = io.StringIO()  # NEW: Buffer for debug logs

            selected_writer.writerow(['Project Title', 'Project Id', 'Mentor Roll Number', 'Mentor Name',
                                    'Mentee Roll Number', 'Mentee Name', 'Avg Rank', 'Mentee Preference'])

            projects = {rank.project for rank in queryset}
            rank_entries = RankList.objects.filter(project__in=projects).select_related(
                'project', 'mentee__user', 'mentor__user'
            )
            log_buffer.write(f"Total RankList entries fetched: {rank_entries.count()}\n")

            unique_mentees = rank_entries.values_list('mentee', flat=True).distinct().count()
            log_buffer.write(f"Total unique mentees in selected projects: {unique_mentees}\n")

            project_data = {
                project.id: {
                    'project': project,
                    'max': int(project.mentee_max),
                    'ranked': defaultdict(lambda: {'ranks': [], 'preferences': []}),
                    'selected': []
                }
                for project in projects
            }

            for entry in rank_entries:
                pid = entry.project.id
                mid = entry.mentee.id
                project_data[pid]['ranked'][mid]['ranks'].append(entry.rank)
                project_data[pid]['ranked'][mid]['preferences'].append(entry.preference)

            for pid, pdata in project_data.items():
                log_buffer.write(f"Project ID {pid} - '{pdata['project'].title}': {len(pdata['ranked'])} mentees ranked\n")

            assigned_mentees = set()
            all_mentees = set()

            for pid, pdata in project_data.items():
                ranked_list = []
                for mentee_id, info in pdata['ranked'].items():
                    freq = len(info['ranks'])
                    avg_rank = mean(info['ranks'])
                    best_pref = min(info['preferences'])
                    ranked_list.append((freq, avg_rank, best_pref, mentee_id))

                ranked_list.sort(key=lambda x: (-x[0], x[1], x[2]))
                pdata['sorted_mentees'] = ranked_list
                all_mentees.update(pdata['ranked'].keys())

                top_5 = ranked_list[:5]
                log_buffer.write(f"Top 5 mentees for Project '{pdata['project'].title}': {top_5}\n")

            for pref in [1, 2, 3]:
                for pdata in project_data.values():
                    for freq, avg_rank, best_pref, mentee_id in pdata['sorted_mentees']:
                        if mentee_id in assigned_mentees or best_pref != pref:
                            continue
                        if len(pdata['selected']) < pdata['max']:
                            pdata['selected'].append({
                                'mentee': Mentee.objects.get(id=mentee_id),
                                'avg_rank': avg_rank,
                                'preference': best_pref,
                                'project': pdata['project']
                            })
                            assigned_mentees.add(mentee_id)

            log_buffer.write(f"Total assigned mentees: {len(assigned_mentees)}\n")
            unassigned_mentees = all_mentees - assigned_mentees
            log_buffer.write(f"Total unassigned mentees: {len(unassigned_mentees)}\n")

            for pdata in project_data.values():
                project = pdata['project']
                mentor_name_str = project.mentor
                project_title_str = project.title

                try:
                    mentor_obj = Mentor.objects.filter(
                        user__name=mentor_name_str,
                    ).filter(
                        projects__title=project_title_str
                    ).select_related('user').distinct().get()

                    mentor_roll_number = mentor_obj.user.roll_number
                except Mentor.DoesNotExist:
                    mentor_roll_number = 'N/A'
                except Mentor.MultipleObjectsReturned:
                    mentor_roll_number = 'Ambiguous'

                for entry in pdata['selected']:
                    selected_writer.writerow([
                        project.title,
                        project.id,
                        mentor_roll_number,
                        mentor_name_str,
                        entry['mentee'].user.roll_number,
                        entry['mentee'].user.name,
                        round(entry['avg_rank'], 2),
                        entry['preference']
                    ])

            selected_writer.writerow([])
            selected_writer.writerow(['--- Unassigned Mentees ---'])
            selected_writer.writerow(['Mentee Roll Number', 'Mentee Name'])

            for mentee_id in unassigned_mentees:
                mentee = Mentee.objects.get(id=mentee_id)
                selected_writer.writerow([
                    mentee.user.roll_number,
                    mentee.user.name
                ])

            zip_file.writestr("selected_mentees.csv", selected_buffer.getvalue())

            # Summary CSV
            summary_buffer = io.StringIO()
            summary_writer = csv.writer(summary_buffer)
            summary_writer.writerow(['Project ID', 'Project Title', 'Max Mentees', 'Selected Count', 'Remaining Slots'])

            for pdata in project_data.values():
                summary_writer.writerow([
                    pdata['project'].id,
                    pdata['project'].title,
                    pdata['max'],
                    len(pdata['selected']),
                    pdata['max'] - len(pdata['selected'])
                ])

            zip_file.writestr("project_summary.csv", summary_buffer.getvalue())

            # NEW: Logs CSV
            log_csv_buffer = io.StringIO()
            log_csv_writer = csv.writer(log_csv_buffer)
            log_csv_writer.writerow(['Debug Logs'])
            for line in log_buffer.getvalue().splitlines():
                log_csv_writer.writerow([line])
            zip_file.writestr("debug_logs.csv", log_csv_buffer.getvalue())
            
                    # Create mentee-level summary buffer
            mentee_summary_buffer = io.StringIO()
            mentee_summary_writer = csv.writer(mentee_summary_buffer)

            # Header row (dynamic up to max 3 preferences maybe)
            header = ['Mentee Roll No', 'Mentee Name']
            max_projects_per_mentee = 3  # or make dynamic
            for i in range(1, max_projects_per_mentee + 1):
                header.extend([
                    f'Project {i} Title', f'Freq {i}', f'Avg Rank {i}', f'Best Pref {i}'
                ])
            header.append('Final Assignment')
            mentee_summary_writer.writerow(header)

            # Build a mapping: mentee_id -> list of rank entries (grouped by project)
            mentee_project_info = defaultdict(lambda: defaultdict(list))
            for entry in rank_entries:
                mentee_project_info[entry.mentee.id][entry.project.id].append(entry)

            # Mentee ID -> Final assigned project title
            assigned_projects_by_mentee = {
                entry['mentee'].id: pdata['project'].title
                for pdata in project_data.values()
                for entry in pdata['selected']
            }

            # Write CSV: one row per mentee
            for mentee_id, project_dict in mentee_project_info.items():
                mentee = Mentee.objects.get(id=mentee_id)
                row = [mentee.user.roll_number, mentee.user.name]

                # Sort project applications by frequency, then avg rank, then pref
                sorted_projects = []
                for pid, entries in project_dict.items():
                    freq = len(entries)
                    avg_rank = round(mean([e.rank for e in entries]), 2)
                    best_pref = min(e.preference for e in entries)
                    sorted_projects.append((freq, avg_rank, best_pref, Project.objects.get(id=pid).title))
                sorted_projects.sort(key=lambda x: (-x[0], x[1], x[2]))

                for i in range(max_projects_per_mentee):
                    if i < len(sorted_projects):
                        freq, avg_rank, best_pref, project_title = sorted_projects[i]
                        row.extend([project_title, freq, avg_rank, best_pref])
                    else:
                        row.extend(['', '', '', ''])

                # Final assignment
                final_assignment = assigned_projects_by_mentee.get(mentee_id, 'Not Assigned')
                row.append(final_assignment)

                mentee_summary_writer.writerow(row)

            # Save this in the ZIP
            zip_file.writestr("mentee_project_summary.csv", mentee_summary_buffer.getvalue())



        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="mentees_and_summary.zip"'
        return response


     # Export selected mentees to CSV action
    @admin.action(description="Export mentees and project summary to ZIP")
    def export_selected_mentees_to_csv_zip(self, request, queryset):
        # Step 0: Setup ZIP buffer
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

            # ---- CSV 1: Selected Mentees ----
            selected_buffer = io.StringIO()
            selected_writer = csv.writer(selected_buffer)

            selected_writer.writerow(['Project Title', 'Project Id', 'Mentor Roll Number', 'Mentor Name',
                                    'Mentee Roll Number', 'Mentee Name', 'Rank Given', 'Mentee Preference'])

            project_slots = {
                project.id: {
                    'project': project,
                    'max': int(project.mentee_max),
                    'selected': []
                }
                for project in {rank.project for rank in queryset}
            }

            assigned_mentees = set()

            unique_mentees1 = RankList.objects.values_list('mentee', flat=True).count()
            print("Total mentee applications:", unique_mentees1)
            
            unique_mentees = RankList.objects.values_list('mentee', flat=True).distinct().count()
            print("Total unique mentees:", unique_mentees)

            
            all_rank_entries = RankList.objects.filter(project__in=[p['project'] for p in project_slots.values()]).order_by('rank', 'preference')

            for rank in all_rank_entries:
                mentee_id = rank.mentee.id
                project_id = rank.project.id

                if mentee_id not in assigned_mentees:
                    if len(project_slots[project_id]['selected']) < project_slots[project_id]['max']:
                        project_slots[project_id]['selected'].append(rank)
                        assigned_mentees.add(mentee_id)

            for slot in project_slots.values():
                for selected in slot['selected']:
                    selected_writer.writerow([
                        selected.project.title,
                        selected.project.id,
                        selected.mentor.user.roll_number,
                        selected.mentor.user.name,
                        selected.mentee.user.roll_number,
                        selected.mentee.user.name,
                        selected.rank,
                        selected.preference
                    ])

            # Add unassigned mentees
            all_mentees = set(RankList.objects.filter(project__in=[p['project'] for p in project_slots.values()]).values_list('mentee', flat=True))
            unassigned_mentees = all_mentees - assigned_mentees

            selected_writer.writerow([])
            selected_writer.writerow(['--- Unassigned Mentees ---'])
            selected_writer.writerow(['Mentee Roll Number', 'Mentee Name'])

            for mentee_id in unassigned_mentees:
                mentee = Mentee.objects.get(id=mentee_id)
                selected_writer.writerow([
                    mentee.user.roll_number,
                    mentee.user.name
                ])

            zip_file.writestr("selected_mentees.csv", selected_buffer.getvalue())


            # ---- CSV 2: Project Summary ----
            summary_buffer = io.StringIO()
            summary_writer = csv.writer(summary_buffer)

            summary_writer.writerow(['Project ID', 'Project Title', 'Max Mentees', 'Selected Count', 'Remaining Slots'])

            for pid, data in project_slots.items():
                summary_writer.writerow([
                    pid,
                    data['project'].title,
                    data['max'],
                    len(data['selected']),
                    data['max'] - len(data['selected'])
                ])

            zip_file.writestr("project_summary.csv", summary_buffer.getvalue())

        # Final ZIP response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="mentees_and_summary.zip"'
        return response



    actions = [export_selected_mentees_to_csv_zip,export_selected_mentees_to_csv]

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

class MenteePreferencesAdmin(admin.ModelAdmin):
    search_fields = ('mentee__user__roll_number',)  # Search by roll number of the mentee

class MenteeWishlistAdmin(admin.ModelAdmin):
    search_fields = ('mentee__user__roll_number',)  # Search by roll number of the mentee
    
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(RankList, RankListAdmin)
admin.site.register(MenteePreference,MenteePreferencesAdmin)
admin.site.register(MenteeWishlist,MenteeWishlistAdmin)

import re

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ('title',)
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
    
    @admin.action(description="Clear all banner images for selected projects")
    def clear_banner_images(self, request, queryset):
        queryset.update(banner_image=None)

    actions = [export_projects_csv,add_co_mentor_as_mentor,clear_banner_images]

# Register the ProjectAdmin with the Django admin panel
admin.site.register(Project, ProjectAdmin)
