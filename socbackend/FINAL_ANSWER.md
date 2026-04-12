### Q1: Does admin.py have an action to link mentors?

**YES!** Two actions:

1. **Existing**: `add_co_mentor_as_mentor` (only co-mentors)
2. **NEW**: `link_all_mentors` (main + co-mentors + creates DomainMembership)

**How to use:**
```
Django Admin → Projects → Projects
→ Select projects (or Select All)
→ Actions → "Link ALL mentors (main + co-mentors) to projects"
→ Click Go
```

This will:
- ✅ Create DomainMembership automatically
- ✅ Create Mentor object automatically
- ✅ Link projects automatically
- ✅ Show success/error messages

---

### Q2: Does user have to "apply as mentor" to see projects?

**NO! Not anymore!** 

### OLD Flow (PROBLEM):
```
1. User registers via SSO
2. CustomUser created
3. UserProfile created
4. User must click "Apply as Mentor" ❌
5. Wait for admin approval ❌
6. DomainMembership created
7. Mentor object created
8. Still no projects linked ❌
```

### NEW Flow (AUTOMATIC):
```
1. User registers via SSO
2. CustomUser created
3. UserProfile created
4. User logs in
5. System finds projects with their roll number
6. DomainMembership created automatically ✅
7. Mentor object created automatically ✅
8. Projects linked automatically ✅
9. User sees projects immediately! ✅
```

**No manual application needed!**

---

## Complete Workflow

### Scenario: Upload CSV with 20 mentors

**Step 1: Upload CSV**
```
Django Admin → Domains → SOC → Bulk Import
Upload CSV with 10 projects, 20 mentors
```

**Step 2: Link existing mentors (Admin Action)**
```
Django Admin → Projects → Projects
→ Filter by domain: SOC
→ Select All
→ Actions → "Link ALL mentors (main + co-mentors) to projects"
→ Click Go

Result:
✓ 12 mentors linked (already registered)
✗ 8 mentors not found (not registered yet)
```

**Step 3: Mentors log in (Automatic)**
```
When the 8 remaining mentors log in:
→ Auto-link function runs
→ DomainMembership created automatically
→ Mentor object created automatically
→ Projects linked automatically
→ They see their projects immediately!
```

**No manual work needed!**

---

## Three Ways to Link Mentors

### Method 1: Admin Action (Manual, One-Time)
```
Django Admin → Projects → Projects
→ Select projects
→ Actions → "Link ALL mentors"
→ Click Go
```
**Use when**: After CSV upload, to link all registered mentors at once

### Method 2: Management Command (Manual, One-Time)
```bash
python manage.py link_mentor_projects --domain=soc
```
**Use when**: Same as Method 1, but from command line

### Method 3: Auto-Link on Login (Automatic, Always)
```
User logs in → Auto-link runs → Projects linked
```
**Use when**: Always! Runs automatically for every login

---

## Key Points

✅ **No manual application needed** - DomainMembership created automatically  
✅ **No admin approval needed** - Auto-approved for mentors in CSV  
✅ **Works for co-mentors too** - All mentors linked  
✅ **Three ways to link** - Admin action, command, or auto-link  
✅ **Idempotent** - Safe to run multiple times  

---

## Summary

**Your CSV has 20 mentors:**
- 12 already registered → Use admin action to link immediately
- 8 not registered → Will auto-link when they first log in

**They don't need to:**
- ❌ Apply as mentor
- ❌ Wait for approval
- ❌ Do anything manually

**They just:**
- ✅ Log in
- ✅ See their projects
- ✅ Start working!


# Mentor Auto-Linking System

## How It Works

### The Problem
When you upload CSV with 20 mentors:
- Projects are created ✅
- But mentors might not be registered yet ❌
- Projects become "orphaned" - exist but no mentor can see them ❌

### The Solution: Auto-Linking

**Two ways to link mentors to projects:**

---

## Method 1: Auto-Link on First Login (Automatic) ✅

**What happens**: When a mentor logs in for the first time, the system automatically searches for projects where their roll number appears and links them.

**How it works**:
1. Mentor logs in via SSO
2. System searches all projects for their roll number
3. Finds matches in `mentor` or `co_mentor_info` fields
4. Creates Mentor object if needed
5. Links all matching projects
6. Mentor sees their projects immediately!

**Example**:
```
CSV uploaded with:
- Project: "AI Chatbot"
- Mentor: "John Doe (21b1234)"

John hasn't registered yet.

Later, John logs in:
1. System finds "21b1234" in project
2. Creates Mentor object for John
3. Links "AI Chatbot" to John
4. John sees project in mentor portal!
```

**Advantages**:
- ✅ Zero manual work
- ✅ Works even if mentor registers months later
- ✅ Handles all domains automatically

---

## Method 2: Manual Linking Command (One-Time) ✅

**Use this**: After uploading CSV, to link all mentors who are already registered.

### Basic Usage

```bash
cd socbackend

# Link all projects in all domains
python manage.py link_mentor_projects

# Link only SOC projects
python manage.py link_mentor_projects --domain=soc

# Dry run (see what would happen without making changes)
python manage.py link_mentor_projects --dry-run
```

### Example Output

```
Processing domain: Summer of Code
Found 10 projects

  ✓ Linked 21b1234 to "AI Chatbot" in soc
  ✓ Linked 21b5678 to "AI Chatbot" in soc (co-mentor)
  ✗ User not found: 21b9999 for project "Web3 DApp"
  ~ 21b1234 already linked to "ML Project"

============================================================
SUMMARY
============================================================
Total projects processed: 10
Successfully linked: 15
Already linked: 3
Mentors not found: 2
Errors: 0

2 mentors not found. They will be auto-linked when they first log in.
```

---

## Complete Workflow

### Scenario: You upload CSV with 20 mentors

**Step 1: Upload CSV**
```bash
Django Admin → Domains → SOC → Bulk Import
Upload CSV with 10 projects, 20 mentors
```

**Step 2: Run linking command**
```bash
python manage.py link_mentor_projects --domain=soc
```

**Result**:
- 12 mentors already registered → Linked immediately ✅
- 8 mentors not registered yet → Will auto-link on first login ✅

**Step 3: Mentors log in**
- 8 remaining mentors log in over next few days
- Each one automatically gets their projects linked
- No manual work needed!

---

## How to Check Mentor Login Status

### In Django Admin

```
Django Admin → Projects → Mentors

Columns:
- Name
- Roll Number
- Phone
- Domain
- Logged In (✅ or ❌)  ← NEW!
- # Projects
- Projects

Filter by: "Last login: Unknown" to see who hasn't logged in
```

### Export to CSV

```
1. Go to Projects → Mentors
2. Select all mentors
3. Actions → "Export selected mentors to CSV"
4. CSV includes "Logged In" column (Yes/No)
```

---

## Understanding `last_login`

**What is it?**
- Built-in Django field on `CustomUser` model
- Automatically set when user logs in
- `NULL` = never logged in
- Timestamp = has logged in

**How it helps:**
- See which mentors haven't logged in yet
- Know who still needs to be contacted
- Track adoption rate
- Identify orphaned projects

**Example**:
```
Mentor A: last_login = 2024-01-15 → ✅ Logged in
Mentor B: last_login = NULL → ❌ Never logged in
```

---

## FAQ

### Q: I uploaded CSV but mentors can't see projects?
**A**: Run `python manage.py link_mentor_projects --domain=soc`

### Q: Some mentors still can't see projects?
**A**: They probably haven't registered yet. They'll auto-link when they first log in.

### Q: How do I know who hasn't logged in?
**A**: Django Admin → Projects → Mentors → Filter by "Last login: Unknown"

### Q: Can I force link a specific mentor?
**A**: Yes, use Django Admin → Projects → Projects → Select project → Actions → "Link co-mentors"

### Q: What if mentor's roll number is wrong in CSV?
**A**: Fix it in Django Admin → Projects → Projects → Edit project → Update mentor field → Run link command again

### Q: Does this work for co-mentors too?
**A**: Yes! Both mentor and co-mentors are auto-linked.

---

## Technical Details

### Auto-Link Logic

```python
def _auto_link_mentor_projects(user):
    # Get user's roll number
    roll = user.profile.roll_number
    
    # Find projects mentioning this roll
    projects = Project.objects.filter(
        Q(mentor__icontains=roll) | 
        Q(co_mentor_info__icontains=roll)
    )
    
    # For each project:
    for project in projects:
        # Verify exact match (not partial)
        if roll_matches_exactly(project, roll):
            # Create Mentor object
            mentor = Mentor.objects.get_or_create(
                user=user.profile,
                domain=project.domain
            )
            # Link project
            mentor.projects.add(project)
```

### When Auto-Link Runs

1. **On SSO Login** (`CustomSSOTokenView.post()`)
2. **On Password Login** (can be added if needed)
3. **Manual Command** (`link_mentor_projects`)

---

## Best Practices

### After CSV Upload

```bash
# 1. Upload CSV
Django Admin → Domains → Bulk Import

# 2. Link existing mentors
python manage.py link_mentor_projects --domain=soc

# 3. Check results
Django Admin → Projects → Mentors
Filter by "Logged In" to see who's missing

# 4. Contact non-logged-in mentors
Export CSV → Email them to log in

# 5. Wait for auto-linking
As they log in, projects auto-link
```

### Regular Monitoring

```bash
# Weekly check
Django Admin → Projects → Mentors
Actions → "Show mentors who have NOT logged in"

# If count is high, send reminder emails
```

---

## Summary

✅ **Auto-link on first login** - Zero manual work  
✅ **Manual command** - Link all at once  
✅ **Login status tracking** - See who's missing  
✅ **Works for co-mentors** - All mentors linked  
✅ **Domain-aware** - Handles multiple domains  
✅ **Error-tolerant** - Continues even if some fail  

**Result**: Mentors see their projects immediately, no matter when they register!
