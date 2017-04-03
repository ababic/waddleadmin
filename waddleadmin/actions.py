from __future__ import unicode_literals

import re

from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured

codename_pattern = re.compile("^([a-z_]+)+$")


class ModelAdminAction(object):

    def __init__(
        self,
        codename,
        model_admin,
        verbose_name='',
        instance_specific=True,
        button_label='',
        button_title='',
        button_url='',
        button_css_classes=[],
        url_registration_required=True,
        url_pattern='',
        view_class=None,
        permissions_required=[],
        template_name='',
    ):
        if not codename_pattern.match(codename):
            raise ImproperlyConfigured(
                "You're trying to register an action with codename '%s' on "
                "your '%s' class. Action codenames must contain only "
                "lower case ascii letters and underscores." % (
                    codename, model_admin.__class__.__name__
                )
            )
        self.codename = codename
        self.model_admin = model_admin
        self.verbose_name = verbose_name
        self.instance_specific = instance_specific
        self.button_label = button_label
        self.button_title = button_title
        self.button_url = button_url
        self.button_css_classes = button_css_classes
        self.url_helper = model_admin.url_helper
        self.url_registration_required = url_registration_required
        self.url_pattern = url_pattern
        self.view_class = view_class
        self.permissions_required = permissions_required
        self.template_name = template_name

    def get_url_pattern(self):
        return self.url_pattern or self.url_helper.get_action_url_pattern(
            self.codename)

    def get_url_name(self):
        return self.url_helper.get_action_url_name(self.codename)

    def get_templates(self):
        if self.template_name:
            return [self.template_name]
        return self.model_admin.get_templates(self.codename)

    def get_view_class(self):
        return self.view_class or getattr(
            self.model_admin, '%s_view_class' % self.codename, None
        )

    def connect_to_view(self, **url_kwargs):
        view_class = self.get_view_class()
        if view_class is None:
            raise ImproperlyConfigured(
                "No view class could be identified for the '%s' action. "
                "Please either add a '%s_view_class' attribute to your '%s' "
                "class or add a 'view_class' value to the action definition "
                "with codename '%s'." % (
                    self.codename,
                    self.codename,
                    self.model_admin.__class__.__name__,
                    self.codename,
                )
            )
        return self.view_class.as_view(self.model_admin)(**url_kwargs)

    @property
    def url(self):
        return url(
            self.get_url_pattern(), self.connect_to_view, self.get_url_name()
        )
