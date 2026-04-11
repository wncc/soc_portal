"""
Bulk import utility for projects from spreadsheet data.
Allows superusers to paste CSV/TSV data directly into Django admin.
"""

import csv
import io
import re
from django.contrib import messages
from django.db import transaction

from accounts.models import UserProfile, CustomUser
from .models import Project, Mentor


def parse_spreadsheet_data(raw_data, delimiter=None):
    """
    Parse raw spreadsheet data (CSV or TSV).
    Auto-detects delimiter if not provided.
    """
    # Auto-detect delimiter
    if delimiter is None:
        first_line = raw_data.split('\n')[0] if raw_data else ''
        tab_count = first_line.count('\t')
        comma_count = first_line.count(',')
        
        if tab_count > comma_count:
            delimiter = '\t'
        else:
            delimiter = ','
    
    reader = csv.DictReader(io.StringIO(raw_data.strip()), delimiter=delimiter)
    rows = list(reader)
    
    # Debug: Print first row keys to check parsing
    if rows:
        print(f"DEBUG: Parsed columns: {list(rows[0].keys())}")
        print(f"DEBUG: First row data: {rows[0]}")
    
    return rows


def extract_mentor_info(mentor_str):
    """
    Extract mentor name and roll from formats like:
    - "John Doe (21b1234)"
    - "21b1234"
    Returns (name, roll) or (None, roll)
    """
    match = re.match(r'([A-Za-z\s]+)\s*\((\w+)\)', mentor_str.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip().lower()
    return None, mentor_str.strip().lower()


def parse_co_mentors(co_mentor_str):
    """
    Parse co-mentor string with multiple mentors:
    "Alice (21b1111), Bob (21b2222)" -> [(Alice, 21b1111), (Bob, 21b2222)]
    """
    if not co_mentor_str or co_mentor_str.upper() == 'NA':
        return []
    
    mentors = []
    for part in co_mentor_str.split(','):
        part = part.strip()
        if part:
            name, roll = extract_mentor_info(part)
            mentors.append((name, roll))
    return mentors


def get_or_create_mentor(roll_number, domain, request):
    """
    Get or create a Mentor object for the given roll number and domain.
    Returns (mentor, created, error_msg)
    """
    try:
        user = CustomUser.objects.get(username=roll_number)
        profile = UserProfile.objects.get(user=user)
        mentor, created = Mentor.objects.get_or_create(
            user=profile,
            domain=domain,
            defaults={'season': '1'}
        )
        return mentor, created, None
    except CustomUser.DoesNotExist:
        return None, False, f"User not found: {roll_number}"
    except UserProfile.DoesNotExist:
        return None, False, f"Profile not found: {roll_number}"
    except Exception as e:
        return None, False, f"Error creating mentor {roll_number}: {str(e)}"


@transaction.atomic
def bulk_import_projects(domain, rows, request):
    """
    Import multiple projects from parsed spreadsheet rows.
    
    Expected columns:
    - title (required)
    - general_category
    - specific_category
    - mentee_max (required)
    - mentor (required) - format: "Name (roll)" or "roll"
    - co_mentors - format: "Name1 (roll1), Name2 (roll2)"
    - weekly_meets
    - description
    - timeline
    - checkpoints
    - prerequisites
    - banner_image_link
    
    Returns (success_count, error_list)
    """
    success_count = 0
    errors = []
    
    print(f"DEBUG: Starting import of {len(rows)} rows into domain {domain.name}")
    
    for idx, row in enumerate(rows, start=2):  # Start from 2 (header is row 1)
        try:
            # Validate required fields
            title = row.get('title', '').strip()
            if not title:
                errors.append(f"Row {idx}: Missing title")
                continue
            
            mentee_max = row.get('mentee_max', '').strip()
            if not mentee_max:
                errors.append(f"Row {idx}: Missing mentee_max")
                continue
            
            mentor_str = row.get('mentor', '').strip()
            if not mentor_str:
                errors.append(f"Row {idx}: Missing mentor")
                continue
            
            print(f"DEBUG: Creating project '{title}' with mentor '{mentor_str}'")
            
            # Create project
            project = Project.objects.create(
                domain=domain,
                title=title,
                general_category=row.get('general_category', 'Others').strip() or 'Others',
                specific_category=row.get('specific_category', 'NA').strip() or 'NA',
                mentee_max=mentee_max,
                mentor=mentor_str,
                co_mentor_info=row.get('co_mentors', 'NA').strip() or 'NA',
                weekly_meets=row.get('weekly_meets', '0').strip() or '0',
                description=row.get('description', 'NA').strip() or 'NA',
                timeline=row.get('timeline', 'NA').strip() or 'NA',
                checkpoints=row.get('checkpoints', 'NA').strip() or 'NA',
                prereuisites=row.get('prerequisites', 'NA').strip() or 'NA',
                banner_image_link=row.get('banner_image_link', '').strip() or None,
            )
            
            print(f"DEBUG: Project created with ID {project.id}")
            
            # Link main mentor
            mentor_name, mentor_roll = extract_mentor_info(mentor_str)
            print(f"DEBUG: Extracted mentor roll: {mentor_roll}")
            
            mentor_obj, created, error = get_or_create_mentor(mentor_roll, domain, request)
            if mentor_obj:
                mentor_obj.projects.add(project)
                print(f"DEBUG: Mentor linked successfully")
            else:
                # Don't fail - just log warning, mentor can be linked later when they register
                errors.append(f"Row {idx} ({title}): Mentor not linked - {error}. Project created, mentor can be linked later.")
                print(f"DEBUG: Mentor not found but project created. Will link when mentor registers.")
            
            # Link co-mentors
            co_mentors = parse_co_mentors(row.get('co_mentors', ''))
            for co_name, co_roll in co_mentors:
                co_mentor_obj, created, error = get_or_create_mentor(co_roll, domain, request)
                if co_mentor_obj:
                    co_mentor_obj.projects.add(project)
                else:
                    # Don't fail - just log warning
                    errors.append(f"Row {idx} ({title}) co-mentor: Not linked - {error}. Will link when they register.")
            
            success_count += 1
            print(f"DEBUG: Row {idx} completed successfully")
            
        except Exception as e:
            import traceback
            error_msg = f"Row {idx}: {str(e)}"
            errors.append(error_msg)
            print(f"DEBUG ERROR: {error_msg}")
            print(f"DEBUG TRACEBACK: {traceback.format_exc()}")
    
    print(f"DEBUG: Import completed. Success: {success_count}, Errors: {len(errors)}")
    return success_count, errors
