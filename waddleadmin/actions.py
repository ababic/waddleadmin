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
        if not title:
            return ''
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

CREATE_ACTION = {
    'instance_specific': False,
    # Translators: A human-friendly version of the 'create' action codename
    'verbose_name': _('add'),
    # Translators: Descriptive 'title' text for 'create' call-to-action links
    'description': 'create a new {model_name_singular}',
    # Translators: The visual text for 'create' call-to-action links
    'button_label': _('add {model_name_singular}'),
    'button_extra_classes': 'bicolor icon icon-plus',
    'permission_required': 'create',
}

INDEX_ACTION = {
    'instance_specific': False,
    # Translators: A human-friendly version of the 'index' action codename
    'verbose_name': _('list'),
    # Translators: Descriptive 'title' text for 'index' call-to-action links
    'description': _('view a list of existing {model_name_plural}'),
    # Translators: The visual link text for 'index' call-to-action links
    'button_label': _('list {model_name_plural}'),
    'permission_required': 'list',
}

INSPECT_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'inspect' action codename
    'verbose_name': _('inspect'),
    # Translators: Descriptive 'title' text for 'inspect' call-to-action links
    'description': _("inspect the {model_name_singular} '{obj}'"),
    # Translators: The visual link text for 'inspect' call-to-action links
    'button_label': _('inspect'),
    'permission_required': 'inspect',
}

EDIT_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'edit' action codename
    'verbose_name': _('edit'),
    # Translators: Descriptive 'title' text for 'inspect' call-to-action links
    'description': _("edit the {model_name_singular} '{obj}'"),
    # Translators: Visual link text for 'edit' call-to-action links
    'button_label': _('edit'),
    'permission_required': 'edit',
}

DELETE_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'delete' action codename
    'verbose_name': _('delete'),
    # Translators: Descriptive 'title' text for 'inspect' call-to-action links
    'description': _("delete the {model_name_singular} '{obj}'"),
    # Translators: Visual link text for 'edit' call-to-action links
    'button_label': _('edit'),
    'button_extra_classes': 'no',
    'permission_required': 'delete',
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
    # Translators: A human-friendly version of the 'choose_parent' action codename
    'verbose_name': _('choose parent page'),
    'permission_required': 'create',
}

ADD_SUBPAGE_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'add_subpage' action codename
    'verbose_name': _('add child page'),
    # Translators: Descriptive 'title' text for 'add_subpage' call-to-action links
    'description': _("add child page to '{obj}'"),
    # Translators: Visual link text for 'add_subpage' call-to-action links
    'button_label': _('add child page'),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

COPY_ACTION = {
    'instance_specific': True,
    #  Translators: A human-friendly version of the 'copy' action codename
    'verbose_name': _('copy'),
    # Translators: Descriptive 'title' text for 'copy' call-to-action links
    'description': _("copy {model_name_singular} '{obj}'"),
    # Translators: Visual link text for 'copy' call-to-action links
    'button_label': _('copy'),
    'permission_required': 'copy',
    'view_url_registration_required': False,
}

MOVE_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'move' action codename
    'verbose_name': _('move'),
    # Translators: Descriptive 'title' text for 'move' call-to-action links
    'description': _("move {model_name_singular} '{obj}'"),
    # Translators: Visual link text for 'move' call-to-action links
    'button_label': _('move'),
    'permission_required': 'move',
    'view_url_registration_required': False,
}

PREVIEW_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'preview' action codename
    'verbose_name': _('preview'),
    # Translators: Descriptive 'title' text for 'move' call-to-action links
    'description': _("preview draft version of '{obj}'"),
    # Translators: Visual link text for 'move' call-to-action links
    'button_label': _('preview'),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

VIEW_LIVE_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'view_live' action codename
    'verbose_name': _('view live'),
    # Translators: Descriptive 'title' text for 'view_live' call-to-action links
    'description': _("view live version of '{obj}'"),
    # Translators: Visual link text for 'view_live' call-to-action links
    'button_label': _('view live'),
    'view_url_registration_required': True,
}

VIEW_DRAFT_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'view_draft' action codename
    'verbose_name': _('view draft'),
    # Translators: Descriptive 'title' text for 'view_draft' call-to-action links
    'description': _("preview draft version of '{obj}'"),
    # Translators: Visual link text for 'view_draft' call-to-action links
    'button_label': _('view draft'),
    'permission_required': 'edit',
    'view_url_registration_required': False,
}

PUBLISH_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'publish' action codename
    'verbose_name': _('publish'),
    # Translators: Descriptive 'title' text for 'publish' call-to-action links
    'description': _("publish '{obj}'"),
    # Translators: Visual link text for 'publish' call-to-action links
    'button_label': _('publish'),
    'permission_required': 'publish',
    'view_url_registration_required': False,
}

UNPUBLISH_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'unpublish' action codename
    'verbose_name': _('unpublish'),
    # Translators: Descriptive 'title' text for 'unpublish' call-to-action links
    'description': _("unpublish '{obj}'"),
    # Translators: Visual link text for 'publish' call-to-action links
    'button_label': _('publish'),
    'permission_required': 'unpublish',
    'view_url_registration_required': False,
}

VIEW_REVISIONS_ACTION = {
    'instance_specific': True,
    # Translators: A human-friendly version of the 'view_revisions' action codename
    'verbose_name': _('view revisions'),
    # Translators: Descriptive 'title' text for 'view_revisions' call-to-action links
    'description': _("view revisions for '{obj}'"),
    # Translators: Visual link text for 'view_revisions' call-to-action links
    'button_label': _('view revisions'),
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
