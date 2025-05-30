"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
# test
from pathlib import Path
import os
import re
from dotenv import load_dotenv
import secrets
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-p4&t4m)l6oje8l8z9l2@lqy&#bwujg!81fc_pa8)+ec28dgrl3')

# SECURITY WARNING: don't run with debug turned on in production!
# Setting DEBUG to True temporarily to see detailed error messages
DEBUG = True

ALLOWED_HOSTS = ['*']  # Allow all hosts temporarily for debugging


# Application definition

INSTALLED_APPS = [
    'jazzmin',  # Django admin theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # "corsheaders",
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_ckeditor_5',  # Updated to CKEditor 5
    'whitenoise.runserver_nostatic',
    'drf_yasg',  # Swagger/OpenAPI documentation
    
    # Local apps
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost:3000",  # React dev
    "https://web-production-f03ff.up.railway.app",  # backend self-call
    "http://web-production-f03ff.up.railway.app",   # backend self-call non-https
    "https://dohblog.vercel.app",  # Your frontend deployment
]

# For development or when you're experiencing CSRF issues, you can temporarily use:
CORS_ALLOW_ALL_ORIGINS = True  # Enable all CORS for debugging

# Enable credentials in CORS requests (important for CSRF)
CORS_ALLOW_CREDENTIALS = True

# More CORS settings
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow these headers in CORS requests
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Try to get frontend URL from environment
FRONTEND_URL = os.environ.get('FRONTEND_URL', '')
if FRONTEND_URL and FRONTEND_URL not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)
    # Also add without trailing slash if present
    if FRONTEND_URL.endswith('/'):
        CORS_ALLOWED_ORIGINS.append(FRONTEND_URL[:-1])
    # Also add with trailing slash if not present
    else:
        CORS_ALLOWED_ORIGINS.append(FRONTEND_URL + '/')

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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# PostgreSQL database configuration
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:TLgjKUteroESAXyyKSkzZeFBRitnmOLq@ballast.proxy.rlwy.net:17918/railway'
)

# Alternative internal connection string (for internal Railway network)
INTERNAL_DB_URL = 'postgresql://postgres:TLgjKUteroESAXyyKSkzZeFBRitnmOLq@postgres.railway.internal:5432/railway'

# Function to mask password for logging
def mask_password(url):
    if not url:
        return "No database URL provided"
    try:
        # Use regex to mask the password
        return re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1*****\3', url)
    except Exception:
        return "Invalid database URL format"

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL in production
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=60)}
    print(f"Using DATABASE_URL from environment: {mask_password(DATABASE_URL)}")
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("Using SQLite for local development")

# Print database configuration for debugging
print(f"Database engine: {DATABASES['default'].get('ENGINE', 'Not specified')}")
print(f"Database name: {DATABASES['default'].get('NAME', 'Not specified')}")
print(f"Database host: {DATABASES['default'].get('HOST', 'Not specified')}")
print(f"Database port: {DATABASES['default'].get('PORT', 'Not specified')}")

# Test database connection function (to be called later, not during initialization)
def test_database_connection():
    import sys
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("Database connection test successful!")
        return True
    except Exception as e:
        print(f"ERROR connecting to database: {str(e)}", file=sys.stderr)
        print(f"Database connection test failed!", file=sys.stderr)
        # Keep the application running even if initial connection fails
        # This allows for troubleshooting through the diagnostic endpoints
        return False

# Don't run this during app initialization, as it leads to the warning
# We'll call this function from a management command or view instead


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CKEditor 5 settings
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                   'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock',
                   'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                   'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                   'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

# CKEditor 5 media upload directory
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "uploads/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# Security settings for production
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False  # Changed to False to rule out potential redirect issues
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Add Railway app domain and frontend domain to CSRF trusted origins
    CSRF_TRUSTED_ORIGINS = [
        'https://web-production-f03ff.up.railway.app',
        'http://web-production-f03ff.up.railway.app',
        'https://dohblog.vercel.app',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://localhost:5174',
    ]
    
    # Add frontend URL to CSRF trusted origins if available
    if FRONTEND_URL:
        frontend_domain = FRONTEND_URL
        if frontend_domain.startswith('http://'):
            frontend_domain = 'http://' + frontend_domain.split('http://')[1]
        elif frontend_domain.startswith('https://'):
            frontend_domain = 'https://' + frontend_domain.split('https://')[1]
        
        if frontend_domain not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(frontend_domain)
else:
    # Even in debug mode, we need CSRF trusted origins for the admin interface
    CSRF_TRUSTED_ORIGINS = [
        'https://web-production-f03ff.up.railway.app',
        'http://web-production-f03ff.up.railway.app',
        'https://dohblog.vercel.app',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://localhost:5174',
    ]

# Jazzmin Admin Theme Settings
JAZZMIN_SETTINGS = {
    # title of the window
    "site_title": "Blog CMS Admin",
    # Title on the login screen
    "site_header": "Blog CMS",
    # Title on the brand (19 chars max)
    "site_brand": "Blog CMS",
    # Logo to use for your site
    "site_logo": None,
    # CSS classes that are applied to the logo
    "site_logo_classes": "img-circle",
    # Relative path to a favicon
    "site_icon": None,
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Blog CMS",
    # Copyright on the footer
    "copyright": "Blog CMS © 2025",
    # The model admin to search from the search bar
    "search_model": ["auth.User", "blog.BlogPost"],
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},
        # App with dropdown menu to all its models pages
        {"app": "blog"},
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    #############
    # User Menu #
    #############
    # Additional links to include in the user menu on the top right
    "usermenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to auto expand the menu
    "navigation_expanded": True,
    # Custom icons for side menu apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "blog.BlogPost": "fas fa-blog",
        "blog.Comment": "fas fa-comments",
        "blog.BlogImage": "fas fa-image",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    ###############
    # Change view #
    ###############
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    # Add a language dropdown into the admin
    "language_chooser": False,
}

# Jazzmin UI Customizations
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# Cookie settings for CSRF protection
CSRF_COOKIE_SAMESITE = 'Lax'  # Use 'Lax' to allow cross-domain requests with CSRF token
SESSION_COOKIE_SAMESITE = 'Lax'  # Same for session cookies
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to access the CSRF cookie
SESSION_COOKIE_HTTPONLY = True  # Don't allow JavaScript to access the session cookie

# Ensure these cookies are accessible from the frontend domain
CSRF_COOKIE_DOMAIN = None  # Let the browser determine based on the request

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/',
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,
    'DEFAULT_MODEL_RENDERING': 'model',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_GENERATOR_CLASS': 'blog.swagger_schema.CustomSchemaGenerator',
    'DEFAULT_AUTO_SCHEMA_CLASS': 'blog.swagger_schema.FileUploadAutoSchema',
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
}
