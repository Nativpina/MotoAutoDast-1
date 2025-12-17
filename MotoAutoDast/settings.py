from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# STATIC LOCAL (DEFAULT)
# ==========================================================

# Se mantiene la lectura de variables, pero la configuración subsiguiente no las usará.
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
AZURE_STATIC_CONTAINER = os.environ.get("AZURE_CONTAINER", "static")

# STATIC URL local. Esta es la URL de acceso que se usará.
STATIC_URL = '/static/'

CSRF_TRUSTED_ORIGINS = [
    "https://motoautodast-dzgvgmfvcaddgzbs.chilecentral-01.azurewebsites.net",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

CSRF_COOKIE_SECURE = True

# Carpeta local que collectstatic llenará (es correcta)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# LOCAL static dir (de tus apps y la carpeta raíz 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Usar WhiteNoise en producción para compresión y cache de largo plazo.
# En desarrollo evitamos los problemas del manifest storage estableciendo
# el storage por defecto cuando DEBUG=True.
DEBUG = os.environ.get("DEBUG", "True") == "True"

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # almacenamiento por defecto en DEV para evitar errores de manifest
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Tiempo de cache que entregará WhiteNoise (en segundos). 1 año por defecto.
WHITENOISE_MAX_AGE = 31536000

# ==========================================================
# MEDIA LOCAL (NO AZURE)
# ==========================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ==========================================================
# DJANGO CONFIG
# ==========================================================

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'custom_admin',
    'MainApp',
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- añadido aquí, justo después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MotoAutoDast.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'MainApp.context_processors.categorias_navbar',
            ],
        },
    },
]

WSGI_APPLICATION = 'MotoAutoDast.wsgi.application'

# ==========================================================
# DATABASE SQLite
# ==========================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================================================
# GENERAL
# ==========================================================
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'login_redirect'
LOGOUT_REDIRECT_URL = 'inicio'

# ==========================================================
# WEBPAY
# ==========================================================
WEBPAY_PLUS_COMMERCE_CODE = os.environ.get("WEBPAY_PLUS_COMMERCE_CODE")
WEBPAY_PLUS_API_KEY = os.environ.get("WEBPAY_PLUS_API_KEY")
WEBPAY_ENV = os.environ.get("WEBPAY_ENV", "TEST")

# ==========================================================
# EMAIL
# ==========================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
