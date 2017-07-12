from __future__ import unicode_literals

import six

from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


class ModelAction(object):

    def __init__(
        self,
        codename,
        model_admin,
        verbose_name='',
        description='',
        instance_specific=True,
        button_label=None,
        button_title=None,
        button_url=None,
        button_extra_classes=None,
        view_class=None,
        view_url_registration_required=True,
        view_url_pattern='',
        view_url_name='',
        permission_required=None,
        template_name='',
        **kwargs
    ):

        self.codename = codename
        self.model_admin = model_admin
        self.url_helper = model_admin.url_helper
        self.model = model_admin.model
        self.verbose_name = verbose_name or codename.replace('_', ' ')
        self.description = description
        self.instance_specific = instance_specific
        self.permission_required = permission_required

        self.button_label = button_label
        self.button_url = button_url
        self.button_title = button_title
        self.button_extra_classes = button_extra_classes

        self.view_class = view_class
        self.view_url_registration_required = view_url_registration_required
        self.view_url_pattern = view_url_pattern
        self.view_url_name = view_url_name
        self.template_name = template_name

        self.init_kwargs = kwargs

    def get_url_pattern(self):
        return self.url_pattern or self.url_helper.get_action_url_pattern(
            self.codename)

    def get_url_name(self):
        return self.url_name or self.url_helper.get_action_url_name(
            self.codename)

    def get_url(self, obj):
        return self.url_helper.get_action_url_for_obj(self.codename, obj)

    def get_templates(self):
        if self.template_name:
            return [self.template_name]
        return self.model_admin.get_templates(self.codename)

    def get_modeladmin_view_method(self):
        return getattr(
            self.model_admin, '%s_view' % self.codename, None
        )

    def get_view_class(self):
        return self.view_class or getattr(
            self.model_admin, '%s_view_class' % self.codename, None
        )

    def format_descriptive_string(self, string, obj):
        return string.format(
            action_name=self.verbose_name,
            model_name_singular=self.model_admin.model_name_singular,
            model_name_plural=self.model_admin.model_name_plural,
            obj=obj,
        )

    def get_description(self, obj):
        return self.format_descriptive_string(self.description, obj)

    def get_button_label(self, obj):
        label = self.button_label or self.verbose_name
        return capfirst(self.format_descriptive_string(label, obj))

    def get_button_title(self, obj):
        title = self.button_title or self.description
        return capfirst(self.format_descriptive_string(title, obj))

    def get_button_url(self, obj):
        return self.button_url or self.get_url(obj)

    def get_button_extra_classes(self, obj, request=None):
        if self.button_extra_classes:
            if isinstance(self.button_extra_classes, six.string_types):
                return self.button_extra_classes.split()
            return list(self.button_extra_classes)
        return []

    def render_view(self, request, *args, **kwargs):
        if self.get_modeladmin_view_method():
            return self.get_modeladmin_view_method(request, *args, **kwargs)

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
        view = self.view_class.as_view(self.model_admin)
        return view(request, *args, **kwargs)

    @property
    def url(self):
        return url(
            self.get_url_pattern(), self.render_view, self.get_url_name()
        )

# Translators: The default description of an action relating to a specific object e.g. "delete the event 'Christmas day'". Used to populate 'title' attributes on button links
default_action_description = _("{action_name} the {model_name_singular} '{obj!s}'")

CREATE_ACTION = {
    'instance_specific': False,
    'verbose_name': _('add'),
    'description': 'Create a new {model_name_singular}',
    'button_label': _('Add {model_name_singular}'),
    'button_extra_classes': 'bicolor icon icon-plus',
    'permission_required': 'create',
    'view_class': 'wagtail.contrib.modeladmin.views.CreateView',
}

INDEX_ACTION = {
    'instance_specific': False,
    'verbose_name': _('list'),
    'description': _('View a list of existing {model_name_plural}'),
    'button_label': _('List {model_name_plural}'),
    'permission_required': 'list',
    'view_class': 'waddleadmin.views.IndexView',
}

INSPECT_ACTION = {
    'instance_specific': True,
    'verbose_name': _('inspect'),
    'description': default_action_description,
    'permission_required': 'inspect',
    'view_class': 'waddleadmin.views.InspectView',
}

EDIT_ACTION = {
    'instance_specific': True,
    'verbose_name': _('edit'),
    'description': default_action_description,
    'permission_required': 'edit',
    'view_class': 'waddleadmin.views.EditView',
}

DELETE_ACTION = {
    'instance_specific': True,
    'verbose_name': _('delete'),
    'description': default_action_description,
    'button_extra_classes': 'no',
    'permission_required': 'delete',
    'view_class': 'waddleadmin.views.DeleteView',
}

DEFAULT_MODEL_ACTIONS = {
    'index': INDEX_ACTION,
    'create': CREATE_ACTION,
    'inspect': INSPECT_ACTION,
    'edit': EDIT_ACTION,
    'delete': DELETE_ACTION,
}

# Page-specific actions

CHOOSE_PARENT_ACTION = {
    'instance_specific': False,
    'verbose_name': _('choose parent page'),
    'description': _('Choose parent page for new {model_name_singular}'),
    'permission_required': 'create',
}

ADD_SUBPAGE_ACTION = {
    'instance_specific': True,
    'verbose_name': _('add child page'),
    'description': _("Add child page to '{obj}'"),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

COPY_ACTION = {
    'instance_specific': True,
    'verbose_name': _('copy'),
    'description': default_action_description,
    'permission_required': 'copy',
    'view_url_registration_required': False,
}

MOVE_ACTION = {
    'instance_specific': True,
    'verbose_name': _('move'),
    'description': default_action_description,
    'permission_required': 'move',
    'view_url_registration_required': False,
}

PREVIEW_ACTION = {
    'instance_specific': True,
    'verbose_name': _('preview'),
    'description': _("Preview draft version of '{obj}'"),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

VIEW_LIVE_ACTION = {
    'instance_specific': True,
    'verbose_name': _('view live'),
    'description': _("View live version of '{obj}'"),
    'view_url_registration_required': True,
}

VIEW_DRAFT_ACTION = {
    'instance_specific': True,
    'verbose_name': _('view draft'),
    'description': _("Preview draft version of '{obj}'"),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

PUBLISH_ACTION = {
    'instance_specific': True,
    'verbose_name': _('publish'),
    'description': default_action_description,
    'permission_required': 'publish',
    'view_url_registration_required': False,
}

UNPUBLISH_ACTION = {
    'instance_specific': True,
    'verbose_name': _('unpublish'),
    'description': default_action_description,
    'permission_required': 'unpublish',
    'view_url_registration_required': False,
}

VIEW_REVISIONS_ACTION = {
    'instance_specific': True,
    'verbose_name': _('view revisions'),
    'description': _("View revisions for {model_name_singular} '{obj}'"),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

DEFAULT_PAGE_MODEL_ACTIONS = {
    'index': INDEX_ACTION,
    'create': CREATE_ACTION,
    'inspect': INSPECT_ACTION,
    'edit': EDIT_ACTION,
    'delete': DELETE_ACTION,
    'choose_parent': CHOOSE_PARENT_ACTION,
    'add_subpage': ADD_SUBPAGE_ACTION,
    'preview': PREVIEW_ACTION,
    'copy': COPY_ACTION,
    'move': MOVE_ACTION,
    'view_draft': VIEW_DRAFT_ACTION,
    'view_live': VIEW_LIVE_ACTION,
    'publish': PUBLISH_ACTION,
    'unpublish': UNPUBLISH_ACTION,
    'revisions_index': VIEW_REVISIONS_ACTION,
}
