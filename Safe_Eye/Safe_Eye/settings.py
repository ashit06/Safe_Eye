import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from a .env file for local development
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY WARNINGS ---
# Keep the secret key used in production secret!
# Get SECRET_KEY from environment variables. The default is for local development ONLY.
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-default-insecure-key-for-local-dev')

# Don't run with debug turned on in production!
# DEBUG should be False in production. Default to 'False' if not set.
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


# --- HOSTS AND CORS CONFIGURATION ---
# Add your deployed backend and frontend URLs.
ALLOWED_HOSTS = ['safe-eye-backend.onrender.com', 'localhost', '127.0.0.1']

# List of trusted origins for POST requests (e.g., from your frontend)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://safe-eye-steo.vercel.app", # Your deployed frontend URL
    "https://safe-eye-backend.onrender.com", # Your deployed backend URL
]

# List of origins that are allowed to make cross-site HTTP requests.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://safe-eye-steo.vercel.app",  # Your frontend URL on Vercel
]
CORS_ALLOW_CREDENTIALS = True


# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Whitenoise for serving static files efficiently in production
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'corsheaders',

    # Your local apps
    'users',
    'incidents',
    'notifications',
    'ai_model',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise Middleware should be placed right after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CORS middleware must be placed before any middleware that can generate responses
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

# --- ASGI and Channels for WebSockets ---
WSGI_APPLICATION = 'Safe_Eye.wsgi.application'
ASGI_APPLICATION = 'Safe_Eye.asgi.application'

# Channel layer configuration for Redis in production
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            # Get Redis URL from environment variables for production
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}


# --- DATABASE ---
# Use dj-database-url to connect to PostgreSQL in production (from DATABASE_URL env var)
# Fallback to SQLite for local development if DATABASE_URL is not set.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600 # Keep database connections alive for 10 minutes
    )
}


# --- AUTHENTICATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
AUTH_USER_MODEL = 'users.CustomUser'


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- STATIC & MEDIA FILES ---
# Static files (CSS, JavaScript, Images for the admin panel)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Directory where `collectstatic` will gather files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User-uploaded content like incident images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- DEFAULT SETTINGS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

