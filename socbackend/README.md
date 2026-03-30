# Backend Setup Guide

Create and configure the .env file before running anything.

## 1. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment using the appropriate command for your operating system (Windows, Linux, or macOS).

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Apply database migrations

```bash
python manage.py migrate
```

## 4. Create a superuser (optional, for Django admin access)

```bash
python manage.py createsuperuser
```

## 5. Load dummy data for local testing

```bash
python manage.py loaddata data.json
```

## 6. Runserver

```bash
python manage.py runserver
```

The data.json file is generated from PostgreSQL data on the ITC server using rclone. The data is synced to Google Drive and then exported as JSON for local SQLite testing.

For more details, read Instructions for dumping data.txt. A separate guide is also available for setting up rclone on ITC servers. If backend data needs to be updated on the servers after a push, you may need to set up rclone again.