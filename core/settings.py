from __future__ import annotations

import hashlib
import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

_render = os.environ.get('RENDER', '').strip().lower() in ('1', 'true', 'yes')
_dbg = os.environ.get('DJANGO_DEBUG', '').strip().lower()
if _dbg in ('1', 'true', 'yes'):
    DEBUG = True
elif _dbg in ('0', 'false', 'no'):
    DEBUG = False
else:
    DEBUG = not _render

_raw_secret = os.environ.get('DJANGO_SECRET_KEY', '').strip()

if DEBUG:
    if not _raw_secret:
        SECRET_KEY = 'django-insecure-local-debug-only-not-for-production'
    else:
        SECRET_KEY = _raw_secret
else:
    if not _raw_secret:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is off (Render: Environment).'
        )
    SECRET_KEY = (
        _raw_secret
        if len(_raw_secret) >= 50
        else hashlib.sha256(_raw_secret.encode('utf-8')).hexdigest()
    )


def _allowed_hosts() -> list[str]:
    if DEBUG:
        return ['localhost', '127.0.0.1', '[::1]']

    hosts: list[str] = []
    render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
    if render_host:
        hosts.append(render_host)
    extra = os.environ.get('ALLOWED_HOSTS', '')
    if extra.strip():
        hosts.extend(part.strip() for part in extra.split(',') if part.strip())
    if not hosts and _render:
        hosts = ['.onrender.com']
    if not hosts:
        raise ImproperlyConfigured(
            'Non-debug mode requires RENDER_EXTERNAL_HOSTNAME, ALLOWED_HOSTS, or Render runtime (RENDER=true).'
        )
    return hosts


ALLOWED_HOSTS = _allowed_hosts()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',

    'users',
    'accounts',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    SECURE_SSL_REDIRECT = False
    _hsts = int(os.environ.get('SECURE_HSTS_SECONDS', '2592000'))
    if _hsts > 0:
        SECURE_HSTS_SECONDS = _hsts
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    _csrf_origins: list[str] = []
    _rh = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
    if _rh:
        _csrf_origins.append(f'https://{_rh}')
    _extra_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
    if _extra_csrf.strip():
        _csrf_origins.extend(p.strip() for p in _extra_csrf.split(',') if p.strip())
    CSRF_TRUSTED_ORIGINS = _csrf_origins

    SILENCED_SYSTEM_CHECKS = [
        'security.W008',
        'security.W021',
    ]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
}
