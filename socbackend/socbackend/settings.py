"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True

load_dotenv(BASE_DIR/".env")

PORTAL_SETTINGS = {
    "CURRENT_ACTIVE_SEASON_ID": 1,
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-d+#y%l^0ihv^!n85jt7ckxco6(b=0(a3+e+fml#3t0ef2gbs3k",
)

ALLOWED_HOSTS = ['socb.tech-iitb.org', 'www.socb.tech-iitb.org', 'itc.gymkhana.iitb.ac.in', 'localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp-auth.iitb.ac.in'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')


AUTH_USER_MODEL = 'accounts.CustomUser'

# Application definition

AUTHENTICATION_BACKENDS = [
    'accounts.customauth.RollNumberBackend',
    'django.contrib.auth.backends.ModelBackend',  # Default backend for user authentication
]

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "accounts",
    "projects",
    "gunicorn",
]

CSRF_TRUSTED_ORIGINS = [
    "https://wncc-soc.tech-iitb.org",
    "https://www.wncc-soc.tech-iitb.org",
    "https://socb.tech-iitb.org",
    "https://www.socb.tech-iitb.org",
    "https://itc.gymkhana.iitb.ac.in",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://wncc-soc.tech-iitb.org",
    "https://www.wncc-soc.tech-iitb.org",
    "https://itc.gymkhana.iitb.ac.in",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
    'PATCH',
]

CORS_ALLOW_HEADERS = [
   'authorization',
    'content-type',
    'x-csrftoken',
    'x-requested-with',
]


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "socbackend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "socbackend.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("accounts.custom_auth.CookieJWTAuthentication",'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "accounts.permissions.HasUserProfile",
    ),
}


SIMPLE_JWT = {
    "AUTH_COOKIE": "auth",
    "ACCESS_TOKEN_LIFETIME": timedelta(days=100000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=100000),
}


IITB_SSO = {
    "TOKEN_URL": "https://gymkhana.iitb.ac.in/sso/oauth/token/",
    "PROFILE_URL": "https://gymkhana.iitb.ac.in/sso/user/api/user/?fields=basic,first_name,last_name,type,program,roll_number",
    "CLIENT_ID": "Ihnr8QIPdQkGC1VRuObDrSOMAjqKM5IXbJji5q62",
    "CLIENT_SECRET_BASE64": "VERGMUh6MUNCN0pVZEd2QVJQb0dYRlRNR3hvbVZPMjRLUVBxaURKdzJ0cmcxTFF1bzhmc2t2ZVVWYUt2b1o5MVhoTDZhMjNHWkRFV3VYUVBPZnNGRklrVlhUem1ISENJb2k3YUxTUW51aXVlRVNQYk9lbmZmaE15M0cxNU9YZ0o==",
}

SSO_BAD_CERT = True  # Set to False if you have a valid certificate
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres:soc2025-praty-veer@wk0g848kcgkckcowkg0ssw4o:5432/postgres'
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

# Media files (only used when DEBUG = True)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000