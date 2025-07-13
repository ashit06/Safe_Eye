# Safe_Eye/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from a .env file for local development
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# These are loaded from environment variables on Render
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a-very-insecure-default-key-for-dev')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# --- HOSTS ---
# Defines which domain names this Django site can serve.
ALLOWED_HOSTS = ['safe-eye-backend.onrender.com', 'localhost', '127.0.0.1']

# --- CORS & CSRF CONFIGURATION (PRODUCTION) ---

# A specific list of origins that are allowed to make cross-site HTTP requests.
# This is the secure, production-ready setting.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://safe-eye-steo.vercel.app", # Your deployed frontend URL
]
CORS_ALLOW_CREDENTIALS = True

# A list of hosts that are trusted for cross-site requests that modify data (e.g., POST).
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://safe-eye-steo.vercel.app", # Your deployed frontend URL
    "https://safe-eye-backend.onrender.com", # Your deployed backend URL
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

# Ensure corsheaders.middleware.CorsMiddleware is placed high up.
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

# This configuration is loaded from the REDIS_URL environment variable on Render.
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [{
                "address": redis_url,
                "ssl": True,
            }],
        },
    },
}

# This configuration is loaded from the DATABASE_URL environment variable on Render.
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