# Summer of Tech Portal - Multi-Domain Architecture

### Official repository for the Summer of Tech Portal (SOC, SOQ, SOR, etc.)
Built using Django REST Framework and React with multi-domain support.

---

## 🏗️ Architecture Overview

### Multi-Domain System
This portal supports multiple independent domains under one platform:
- **SOC** (Summer of Code)
- **SOQ** (Summer of Quants)
- **SOR** (Summer of Robotics)
- And more...

### Key Features
- **One User Account**: Each user has ONE account across all domains
- **Multiple Roles**: Users can be mentor in SOC, mentee in SOQ, manager for all domains
- **Domain Independence**: Each domain has its own projects, mentors, mentees
- **Centralized Management**: Platform managers can create and manage all domains
- **Bulk Project Import**: Upload CSV/TSV/Excel files to import multiple projects at once
- **Domain-Specific Project IDs**: Each domain has its own project numbering (SOC #1, SOQ #1, etc.)
- **Mentor Contact Info**: Phone numbers visible on project pages for mentee communication
- **Consistent Navigation**: Quick access bar on all mentee portal pages

### Database Models

#### Core Models
- **CustomUser**: Django auth user (one per roll number)
- **UserProfile**: Extended profile (name, roll, phone, year, department)

#### Domain Models
- **Domain**: Represents a tech domain (slug, name, description, permissions)
- **DomainMembership**: Links user to domain with role (mentor/mentee/manager)

#### Project Models
- **Project**: Domain-scoped projects
- **Mentor**: Domain-scoped mentor profiles
- **Mentee**: Domain-scoped mentee profiles
- **MenteeWishlist**: Mentee's project wishlist
- **MenteePreference**: Mentee's project preferences with SOP
- **RankList**: Project-level mentee rankings (shared by all co-mentors)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (production) or SQLite (development)
- pnpm (recommended) or npm

---

## 📦 Backend Setup

### 1. Navigate to backend directory
```bash
cd socbackend
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

**For Excel support in bulk import:**
```bash
pip install openpyxl
```

### 5. Create `.env` file
Copy `.env.example` to `.env` and configure:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
MANAGER_SECRET_TOKEN=your-manager-secret-token
EMAIL_HOST_USER=your-email@example.com
```

### 6. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Load sample data (optional)
```bash
python manage.py loaddata data2.json
```

### 8. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 9. Run development server
```bash
python manage.py runserver
```

Backend will be available at: `http://127.0.0.1:8000`

---

## 🎨 Frontend Setup

### 1. Navigate to frontend directory
```bash
cd socfrontend
```

### 2. Install pnpm globally (if not installed)
```bash
npm install -g pnpm
```

### 3. Install dependencies
```bash
pnpm install
```

### 4. Create `.env` file
Copy `.env.example` to `.env` and configure:
```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8000/api
REACT_APP_API_URL=http://127.0.0.1:8000
```

### 5. Start development server
```bash
pnpm start
```

Frontend will be available at: `http://localhost:3000`

---

## 💾 Data Management

### Dumping Data 

**Dump all data:**
```bash
python manage.py dumpdata > data.json
```

**Dump specific apps only (recommended):**
```bash
python manage.py dumpdata accounts domains projects --indent 2 > data.json
```

**Exclude sensitive data:**
```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > data.json
```

**Exclude sessions (recommended):**
```bash
python manage.py dumpdata --exclude sessions --exclude admin.logentry --indent 2 > data.json
```

### Loading Data (For New Setup)

**After running migrations:**
```bash
python manage.py loaddata data.json
```

### Best Practice for GitHub
1. Dump data without sessions and logs:
```bash
python manage.py dumpdata accounts domains projects --exclude sessions --exclude admin.logentry --indent 2 > data.json
```

2. Commit `data.json` to repository
3. New contributors can load it after migrations

---

## 🔐 Initial Setup for New Contributors

### 1. Clone repository
```bash
git clone <repository-url>
cd soc_portal
```

### 2. Setup backend
```bash
cd socbackend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata data.json  # Load sample data
python manage.py runserver
```

### 3. Setup frontend (in new terminal)
```bash
cd socfrontend
pnpm install
pnpm start
```

### 4. Access the application
- Frontend: `http://localhost:3000`
- Backend API: `http://127.0.0.1:8000/api`
- Admin Panel: `http://127.0.0.1:8000/admin`

---

## 👥 User Roles & Access

### Platform Manager
- **Access**: All domains
- **Permissions**: 
  - Create/edit/delete domains
  - Approve mentor applications
  - Manage members
  - Toggle project creation/editing permissions
- **How to become**: Visit `/become-manager/<secret-token>` (token set in .env)

### Domain Manager
- **Access**: Specific domain(s)
- **Permissions**: Same as platform manager but for assigned domains only

### Mentor
- **Access**: Specific domain(s)
- **Permissions**:
  - Create projects (if enabled by manager)
  - Edit projects (if enabled by manager)
  - View mentee applications
  - Rank mentees
  - Manage project mentees

### Mentee
- **Access**: Specific domain(s)
- **Permissions**:
  - Browse projects
  - Add projects to wishlist
  - Submit project preferences with SOP

---

## 🌐 Domain-Scoped Routes

### Public Routes
- `/` - Home page with domain cards
- `/login` - SSO login

### Manager Routes
- `/manager` - Manager dashboard
- `/become-manager/:secret` - Manager bootstrap URL

### Mentee Routes (Domain-Scoped)
- `/:domain/current_projects` - Browse projects
- `/:domain/current_projects/:id` - Project details
- `/:domain/wishlist` - View wishlist
- `/:domain/PreferenceForm` - Submit preferences

### Mentor Routes (Domain-Scoped)
- `/:domain/mentor/home` - Mentor dashboard
- `/:domain/mentor/add-project` - Create new project
- `/:domain/mentor/edit-project` - Edit existing project

### Legacy Routes (Backward Compatible)
- `/current_projects` - Works if user has only one mentee membership
- `/mentor/home` - Works if user has only one mentor membership

---

## 🔧 API Endpoints

### Authentication
- `POST /api/accounts/register_sso/` - Register via SSO
- `POST /api/accounts/token_sso/` - Get auth token
- `GET /api/accounts/isloggedin/` - Check login status
- `GET /api/accounts/my-memberships/` - Get user's memberships

### Domains
- `GET /api/domains/` - List active domains (public)
- `POST /api/domains/` - Create domain (managers only)
- `GET /api/domains/<slug>/` - Domain detail
- `PATCH /api/domains/<slug>/` - Edit domain (managers only)
- `GET /api/domains/<slug>/projects/` - List domain projects

### Domain Membership
- `GET /api/domains/<slug>/members/` - List members (managers only)
- `POST /api/domains/<slug>/members/` - Apply for membership
- `PATCH /api/domains/<slug>/members/<id>/` - Approve membership (managers only)

### Projects (Domain-Scoped)
- `GET /api/projects/?domain=<slug>` - List projects for domain
- `GET /api/projects/<id>/` - Project detail (includes `display_id`, `mentor_details`, `co_mentor_details`)
- `POST /api/projects/mentor/profile/` - Create project (mentor)
- `PUT /api/projects/mentor/profile/<id>/` - Edit project (mentor)

### Wishlist & Preferences (Domain-Scoped)
- `GET /api/projects/wishlist/?domain=<slug>` - Get wishlist
- `POST /api/projects/wishlist/` - Add to wishlist
- `DELETE /api/projects/wishlist/?project_id=X&domain=slug` - Remove from wishlist
- `GET /api/projects/preference/?domain=<slug>` - Get preferences
- `POST /api/projects/preference/` - Submit preference

### Bulk Import (Admin Only)
- Access via Django Admin → Domains → Bulk Import button
- Supports CSV, TSV, XLSX, XLS file formats
- Auto-creates projects and links mentors

---

## 📚 Documentation

### API Documentation
Access interactive API docs:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

### Frontend Documentation
Generate component documentation using Storybook:
```bash
cd socfrontend
npm install --save-dev @storybook/react
npx sb init
npx storybook
```

### Backend Code Documentation
Generate Sphinx documentation:
```bash
cd socbackend/docs
./make.bat html  # Windows
make html        # Linux/macOS
```
Open `socbackend/docs/_build/html/index.html` in browser

---

## 🎯 Common Workflows

### Creating a New Domain (Manager)
1. Login and navigate to `/manager`
2. Click "New Domain"
3. Fill in details:
   - Slug: `soq` (unique identifier)
   - Name: `Summer of Quants`
   - Description: Domain description
   - Upload cover photo
4. Toggle registration settings:
   - ✅ Mentee Registration Open
   - ✅ Mentor Registration Open
5. Toggle project permissions:
   - ✅ Allow mentors to create projects
   - ✅ Allow mentors to edit projects
6. Save

### Bulk Importing Projects (Superuser)
1. Go to Django Admin → Domains
2. Click "📋 Bulk Import" button next to target domain
3. Choose import method:
   - **Option 1**: Upload CSV/TSV/Excel file
   - **Option 2**: Paste spreadsheet data
4. Click "Import Projects"
5. Review results:
   - ✅ Success count
   - ⚠️ Warnings (e.g., mentor not found - project still created)
6. Projects appear with domain-specific IDs (e.g., SOC #1, SOC #2)

**Template Format:**
```csv
title,mentee_max,mentor,co_mentors,description
AI Chatbot,3,John Doe (21b1234),Alice (21b5678),Build a chatbot
Web3 DApp,2,Sarah (21b3456),NA,Create a DApp
```

**Documentation:**
- `socbackend/projects/TEMPLATE.csv` - CSV template
- `socbackend/projects/TEMPLATE.tsv` - TSV template
- `socbackend/projects/BULK_IMPORT_GUIDE.md` - Complete guide
- `socbackend/projects/QUICK_REFERENCE.md` - Quick reference

### Applying as Mentor
1. Login via SSO
2. Click on domain card (e.g., "Summer of Code")
3. Click "Apply as Mentor"
4. Wait for manager approval
5. Once approved, access mentor portal via "My Domains" dropdown

### Registering as Mentee
1. Login via SSO
2. Click on domain card (e.g., "Summer of Code")
3. Click "Register as Mentee" (auto-approved)
4. Redirected to `/soc/current_projects`
5. Browse projects, add to wishlist, submit preferences

### Creating a Project (Mentor)
1. Navigate to `/:domain/mentor/home`
2. Click "Add Project" card (only visible if creation is enabled)
3. Fill project details:
   - Title, category, description
   - Number of mentees
   - Co-mentors (optional)
   - Timeline, checkpoints, prerequisites
   - Banner image link
4. Submit

### Ranking Mentees (Mentor)
1. Navigate to `/:domain/mentor/home`
2. Click on a project card
3. View list of mentees who applied
4. Drag and drop to rank mentees
5. Save ranklist
6. **Note**: Co-mentors see and share the same ranklist

---

## 🐛 Troubleshooting

### Backend Issues

**Migration conflicts:**
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

**Database locked (SQLite):**
```bash
# Stop all Django processes
# Delete db.sqlite3
python manage.py migrate
python manage.py loaddata data.json
```

**Module not found:**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Port already in use:**
```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Kill process on port 3000 (Linux/macOS)
lsof -ti:3000 | xargs kill -9
```

**Dependencies not installing:**
```bash
rm -rf node_modules package-lock.json
pnpm install
```

**Environment variables not loading:**
- Ensure `.env` file exists in `socfrontend/`
- Restart development server after changing `.env`

---

## 🔒 Security Notes

### For Production Deployment
1. Set `DEBUG=False` in backend `.env`
2. Use PostgreSQL instead of SQLite
3. Set strong `SECRET_KEY` and `MANAGER_SECRET_TOKEN`
4. Configure CORS properly
5. Use HTTPS
6. Set up proper authentication (SSO)
7. Never commit `.env` files to Git

### Sensitive Data
- `.env` files are in `.gitignore`
- `data.json` should NOT contain real user passwords
- Manager secret tokens should be rotated regularly

---

## 📝 Contributing

### Before Making a Pull Request
1. Run migrations and ensure no conflicts
2. Test all affected features
3. Update documentation if needed
4. Follow code style guidelines
5. Write meaningful commit messages

### Code Style
- **Backend**: Follow PEP 8 (Python)
- **Frontend**: Follow Airbnb React/JSX Style Guide
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions

### Testing Checklist
- [ ] Backend migrations apply cleanly
- [ ] Frontend builds without errors
- [ ] All API endpoints work with domain parameter
- [ ] Domain-scoped routes navigate correctly
- [ ] URLGuard properly restricts access
- [ ] Manager dashboard functions work
- [ ] Mentor portal shows correct permissions
- [ ] Mentee portal shows domain-specific projects

---

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Contact Web and Coding Club, IIT Bombay
- Check existing documentation in `/docs` folder

---

## 📄 License

This project is maintained by the Web and Coding Club, IIT Bombay.

---

## 🙏 Acknowledgments

- **TTY17** - Original SoC Portal creators
- **HelloFOSS '24** - Contributing community
- **Web and Coding Club, IIT Bombay** - Project maintainers

---

## 📊 Project Structure

```
soc_portal/
├── socbackend/                 # Django REST Framework backend
│   ├── accounts/              # User authentication & profiles
│   ├── domains/               # Domain management
│   │   ├── admin.py           # Includes bulk import action
│   │   └── templates/         # Bulk import form template
│   ├── projects/              # Projects, mentors, mentees
│   │   ├── bulk_import.py     # Bulk import logic
│   │   ├── TEMPLATE.csv       # CSV template
│   │   ├── TEMPLATE.tsv       # TSV template
│   │   ├── BULK_IMPORT_GUIDE.md
│   │   ├── QUICK_REFERENCE.md
│   │   └── TEMPLATES_SUMMARY.md
│   ├── socbackend/            # Django settings
│   ├── manage.py
│   ├── requirements.txt
│   └── data.json              # Sample data dump
│
├── socfrontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # Shared components
│   │   ├── home/              # Home page & domain cards
│   │   ├── manager/           # Manager dashboard
│   │   ├── mentor/            # Mentor portal
│   │   ├── mentee/            # Mentee portal (with navigation bar)
│   │   │   ├── pages/
│   │   │   │   ├── Projects.jsx       # Shows mentor phone numbers
│   │   │   │   ├── Wishlist.jsx       # With navigation bar
│   │   │   │   ├── PreferenceForm.jsx # With navigation bar
│   │   │   │   └── ProjectDetails.jsx # Shows domain project ID
│   │   ├── utils/             # API utilities
│   │   ├── App.js             # Main app with routing
│   │   └── URLGuard.js        # Route protection
│   ├── package.json
│   └── .env.example
│
├── README.md                  # Original README
├── README2.md                 # This comprehensive guide
└── CONTRIBUTING.md            # Contribution guidelines
```

---

## 🚦 Quick Start Summary

```bash
# Backend
cd socbackend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata data.json
python manage.py runserver

# Frontend (new terminal)
cd socfrontend
pnpm install
pnpm start

# Access
# Frontend: http://localhost:3000
# Backend: http://127.0.0.1:8000
```

Happy coding! 🎉
