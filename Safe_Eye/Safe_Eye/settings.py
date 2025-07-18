# Safe_Eye/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from datetime import timedelta
import certifi # Import the certifi package
import ssl # Import the ssl module for SSL configuration

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a-very-insecure-default-key-for-dev')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['safe-eye-backend.onrender.com', 'localhost', '127.0.0.1','testserver']

# --- CORS & CSRF CONFIGURATION (PRODUCTION) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://safe-eye-steo.vercel.app",
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://safe-eye-steo.vercel.app",
    "https://safe-eye-backend.onrender.com",
]

# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'corsheaders',
    'users',
    'incidents',
    'notifications',
    'ai_model',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'Safe_Eye.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Safe_Eye.wsgi.application'
ASGI_APPLICATION = 'Safe_Eye.asgi.application'

# --- THIS IS THE FINAL FIX ---
# This configuration explicitly tells the Redis client to use certifi's
# certificate bundle for SSL verification.

# Get the base URL from the environment
REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    # This fix is still required for Railway's Redis
    CELERY_BROKER_URL = f"{REDIS_URL}?ssl_cert_reqs={ssl.CERT_NONE}"
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": { "hosts": [f"{REDIS_URL}?ssl_cert_reqs={ssl.CERT_NONE}"], },
        },
    }
else:
    # This block ensures your app still works for local development
    # by falling back to a standard, non-secure Redis URL.
    CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": ["redis://127.0.0.1:6379"],
            },
        },
    }

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
AUTH_USER_MODEL = 'users.CustomUser'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Celery Configuration
# Use the same Redis instance as your Channels layer
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'


# --- EMAIL CONFIGURATION (SMTP for Production) ---
# This configuration uses SMTP to send real emails.
# It is crucial to use environment variables to keep your credentials secure.
# Do NOT hardcode your email or password in this file.
#
# For Gmail, you MUST generate an "App Password".
# 1. Go to your Google Account settings.
# 2. Go to "Security".
# 3. Enable 2-Step Verification.
# 4. Go to "App passwords", create a new password for this app, and use it below.

# Set to 'True' in your environment to enable SMTP.
USE_SMTP = os.environ.get('USE_SMTP', 'False') == 'True'

if USE_SMTP:
    print("✅ SMTP is enabled. Attempting to use real email configuration.")
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')  # e.g., 'smtp.gmail.com'
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # Your full email address
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Your App Password
else:
    # --- Fallback for Development ---
    # Emails will be printed to the console where you run the server.
    print("-------------------------------------------------")
    print("WARNING: SMTP not configured. Emails will be printed to the console.")
    print("To send real emails, set USE_SMTP=True and other EMAIL_* variables in your environment.")
    print("-------------------------------------------------")
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# This is the "From" address that will appear on the emails.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Safe Eye Alert <noreply@safe-eye.com>')

