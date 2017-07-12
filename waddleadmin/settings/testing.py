from .base import *  # NOQA

DEBUG = False
SITE_ID = 1

DATABASES = {
    'default': {
        'NAME': 'waddleadmin-testing.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS += (
    'wagtail.tests.testapp',
    'waddleadmin.tests',
)

ROOT_URLCONF = 'waddleadmin.tests.urls'
WAGTAIL_SITE_NAME = 'waddleadmin Test'
