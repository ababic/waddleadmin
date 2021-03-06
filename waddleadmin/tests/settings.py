"""
Settings for test app
"""
import os
from django.conf.global_settings import *  # NOQA

WAGTAIL_SITE_NAME = 'WaddleAdmin Testing'
ROOT_URLCONF = 'waddleadmin.tests.urls'
DEBUG = False

DATABASES = {
    'default': {
        'NAME': 'waddleadmin-testing.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'wagtail.contrib.settings',
    'wagtail.wagtailforms',
    'wagtail.wagtailsearch',
    'wagtail.wagtailembeds',
    'wagtail.wagtailimages',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailsnippets',
    'wagtail.wagtaildocs',
    'wagtail.wagtailredirects',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtail.contrib.modeladmin',
    'wagtail.tests.testapp',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'django_extensions',
    'taggit',
    'modelcluster',

    # Waddleadmin apps
    'waddleadmin',
    'waddleadmin.tests',
)

TIME_ZONE = 'Europe/London'
USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en'

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
SECRET_KEY = 'not-needed'
LOGIN_URL = 'wagtailadmin_login'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)
SITE_ID = 1

# =============================================================================
# Templates
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
