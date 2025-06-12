from pathlib import Path
import os
import re
from dotenv import load_dotenv
import dj_database_url
from datetime import timedelta

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'a!x(mhy4kdh(r(*%)tw5cb5n%y4u%l*gtwuc-j=b&!kdohs-u5')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Dynamically set allowed hosts from env
allowed_hosts_env = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = allowed_hosts_env.split(",")

# Always allow Railway domains - explicitly add these regardless of what's in the env var
railway_domains = [
    ".railway.app",
    "*.railway.app",
    "*.up.railway.app",
    "*-production-*.up.railway.app",
    "backend-production-49ec.up.railway.app"
]

for domain in railway_domains:
    if domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(domain)

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_ckeditor_5',
    'whitenoise.runserver_nostatic',
    'drf_yasg',

    # Local apps
    'blog',
    'health',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Enable in production if needed
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    None  # Default to None so we can fall back to SQLite
)

def mask_password(url):
    if not url:
        return "No database URL provided"
    try:
        return re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1*****\3', url)
    except Exception:
        return "Invalid database URL format"

if DATABASE_URL:
    print(f"Using DATABASE_URL from environment: {mask_password(DATABASE_URL)}")
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL, 
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    print("WARNING: No DATABASE_URL found. Using SQLite for local development only. Add a DATABASE_URL to your environment.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Change to a storage class that doesn't break on missing files
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
CORS_ALLOW_CREDENTIALS = True  # Allow credentials

# Get CORS allowed origins from environment or use a default list
cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
# If env variable is empty, add some sensible defaults
if not cors_origins or cors_origins == [""]:
    cors_origins = [
        "https://backend-production-49ec.up.railway.app",
        "http://localhost:3000",
        "https://dohblog.vercel.app"
    ]
CORS_ALLOWED_ORIGINS = cors_origins

# CSRF Trusted Origins
csrf_trusted_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
if not csrf_trusted_origins or csrf_trusted_origins == [""]:
    csrf_trusted_origins = [
        "https://backend-production-49ec.up.railway.app",
        "http://localhost:3000",
        "https://dohblog.vercel.app"
    ]
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins

# Additional CORS settings for preflight requests
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow all headers in requests
CORS_ALLOW_ALL_HEADERS = True

# Add a middleware to inject CORS headers for all responses
class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Add CORS headers to all responses
        origin = request.META.get('HTTP_ORIGIN', '')
        if origin and (origin in CORS_ALLOWED_ORIGINS or CORS_ALLOW_ALL_ORIGINS):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            # Handle preflight requests
            if request.method == 'OPTIONS':
                response["Access-Control-Max-Age"] = "86400"  # 24 hours
        return response

# Add the custom middleware to the middleware list
if "CorsMiddleware" not in str(MIDDLEWARE):
    MIDDLEWARE.append('backend.settings.CorsMiddleware')

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CKEditor 5
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link', 'bulletedList',
            'numberedList', 'blockQuote', 'imageUpload',
        ],
    }
}
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "uploads/ckeditor/"

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {'basic': {'type': 'basic'}},
    'USE_SESSION_AUTH': False,
    'VALIDATOR_URL': None,
    'DEFAULT_INFO': 'backend.urls.api_info',
}

# Logging
DJANGO_LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'blog': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'health': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'asgi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'wsgi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Make sure corsheaders middleware is first
if 'corsheaders.middleware.CorsMiddleware' in MIDDLEWARE:
    # Remove it first to avoid duplicates
    MIDDLEWARE.remove('corsheaders.middleware.CorsMiddleware')
# Add it at the beginning
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# Add additional CORS settings
CORS_URLS_REGEX = r'^/api/.*$'
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours in seconds

# Make sure your Django application is listening on the PORT environment variable provided by Railway
# The application should bind to 0.0.0.0 or :: (for IPv6) and use the PORT environment variable
