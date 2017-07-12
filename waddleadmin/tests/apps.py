from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class WagtailTestsAppConfig(AppConfig):
    name = 'waddleadmin.tests'
    label = 'waddleadmin_test'
    verbose_name = "WaddleAdmin Test App"
