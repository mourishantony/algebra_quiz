"""
Django settings for algebra_quiz_proj — No database version.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-x$4*5&+7^gzwswxm)64egufvsi+wjgo5zsb8=38u5snn=lh5cg')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allow all hosts on Render, or specific hosts if ALLOWED_HOSTS is set
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',') if os.environ.get('ALLOWED_HOSTS') else ['*']

# ── Minimal apps — no DB-dependent apps ───────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'quiz',
]

# ── Minimal middleware — no session / auth middleware ─────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'algebra_quiz_proj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'algebra_quiz_proj.wsgi.application'

# ── No database ──────────────────────────────────────────────────────────
# The quiz app never reads or writes a database.
# A minimal in-memory SQLite entry is kept only so Django's test runner
# (which always calls flush/teardown) does not crash.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# ── Internationalization ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ── Static files ──────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
