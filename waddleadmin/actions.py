from __future__ import unicode_literals

import re
import six

from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

codename_pattern = re.compile("^([a-z_]+)+$")


class ModelAdminAction(object):

    def __init__(
        self,
        codename,
        model_admin,
        verbose_name='',
        instance_specific=True,
        button_label=None,
        button_title=None,
        button_url=None,
        button_extra_classes=None,
        view_class=None,
        view_url_registration_required=True,
        view_url_pattern='',
        view_url_name='',
        view_permissions_required=[],
        template_name='',
    ):

        if not codename_pattern.match(codename):
            raise ImproperlyConfigured(
                "You're trying to register an action with codename '%s' on "
                "your '%s' class. Action codenames must contain only "
                "lower case ascii letters and underscores" % (
                    codename, model_admin.__class__.__name__
                )
            )

        if codename in model_admin._actions.keys():
            if model_admin.model_actions:
                raise ImproperlyConfigured(
                    "Your '%s' class has more than one model actions defined "
                    "with the codename '%s'. Model action definitions must "
                    "have unique codenames" % (
                        model_admin.__class__.__name__, codename
                    )
                )
            raise ImproperlyConfigured(
                "Your '%s' class has more than one model actions defined with "
                "the codename '%s'. Model action definitions must have unique "
                "codenames. If you wish to override default model actions, "
                "try using the `model_actions` attribute instead of "
                "`extra_model_actions`" % (
                    model_admin.__class__.__name__, codename
                )
            )

        self.codename = codename
        self.model_admin = model_admin
        self.model = model_admin.model
        self.verbose_name = verbose_name or codename.replace('_', ' ')
        self.instance_specific = instance_specific
        self.button_label = button_label
        self.button_title = button_title
        self.button_url = button_url
        self.button_extra_classes = button_extra_classes
        self.url_helper = model_admin.url_helper
        self.view_class = view_class
        self.view_url_registration_required = view_url_registration_required
        self.view_url_pattern = view_url_pattern
        self.view_url_name = view_url_name
        self.view_permissions_required = view_permissions_required
        self.template_name = template_name

    @cached_property
    def url_definition(self):
        return url(
            self.get_url_pattern(), self.connect_to_view, self.get_url_name()
        )

    def get_url_pattern(self):
        return self.url_pattern or self.url_helper.get_action_url_pattern(
            self.codename)

    def get_url_name(self):
        return self.url_name or self.url_helper.get_action_url_name(
            self.codename)

    def get_url_for_obj(self, obj):
        return self.url_helper.get_action_url_for_obj(self.codename, obj)

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

    def get_button_label_for_obj(self, obj):
        if self.button_label:
            if callable(self.button_label):
                try:
                    return self.button_label(obj, self.model)
                except TypeError:
                    try:
                        return self.button_label(obj)
                    except TypeError:
                        return self.button_label()
            return self.button_label
        return

    def get_button_title_for_obj(self, obj):
        if self.button_title:
            if callable(self.button_title):
                try:
                    return self.button_title(obj, self.model)
                except TypeError:
                    try:
                        return self.button_title(obj)
                    except TypeError:
                        return self.button_title()
            return self.button_title
        return

    def get_button_url_for_obj(self, obj):
        if self.button_url:
            if callable(self.button_url):
                try:
                    return self.button_url(obj, self.model)
                except TypeError:
                    try:
                        return self.button_url(obj)
                    except TypeError:
                        return self.button_url()
            return self.button_url
        return self.get_url_for_obj(obj)

    def get_button_extra_classes_for_obj(self, obj):
        if self.button_extra_classes:
            if callable(self.button_extra_classes):
                try:
                    return self.button_extra_classes(obj, self.model)
                except TypeError:
                    try:
                        return self.button_extra_classes(obj)
                    except TypeError:
                        return self.button_extra_classes()
            if isinstance(self.button_extra_classes, six.string_types):
                return self.button_extra_classes.split()
            return list(self.attr)
        return []


CREATE_ACTION = ('create', {
    'verbose_name': _('add'),
    'instance_specific': False,
    'button_extra_classes': 'bicolor icon icon-plus',
    'view_permissions_required': ['create']
})

INDEX_ACTION = ('index', {
    'verbose_name': _('list'),
    'instance_specific': False,
    'view_permissions_required': ['list'],
})

INSPECT_ACTION = ('inspect', {
    'verbose_name': _('inspect'),
    'view_permissions_required': ['inspect'],
})

EDIT_ACTION = ('edit', {
    'verbose_name': _('edit'),
    'view_permissions_required': ['edit'],
})

DELETE_ACTION = ('delete', {
    'verbose_name': _('delete'),
    'button_extra_classes': 'no',
    'view_permissions_required': ['delete'],
})

DEFAULT_MODEL_ACTIONS = [INDEX_ACTION, CREATE_ACTION, INSPECT_ACTION,
                         EDIT_ACTION, DELETE_ACTION]

# Page-specific actions

CHOOSE_PARENT_ACTION = ('choose_parent', {
    'verbose_name': _('choose parent page'),
    'instance_specific': False,
    'view_permissions_required': ['create']
})

ADD_SUBPAGE_ACTION = ('add_subpage', {
    'verbose_name': _('add sub-page'),
    'view_url_registration_required': False,
    'view_permissions_required': ['edit'],
})

COPY_ACTION = ('copy', {
    'verbose_name': _('copy'),
    'view_permissions_required': ['copy'],
    'view_url_registration_required': False,
})

MOVE_ACTION = ('move', {
    'verbose_name': _('move'),
    'view_permissions_required': ['edit'],
    'view_url_registration_required': False,
})

PREVIEW_ACTION = ('preview', {
    'verbose_name': _('preview'),
    'view_permissions_required': ['edit'],
    'view_url_registration_required': False,
})

VIEW_DRAFT_ACTION = ('view_draft', {
    'verbose_name': _('view draft'),
    'view_permissions_required': ['edit'],
    'view_url_registration_required': False,
})

PUBLISH_ACTION = ('publish', {
    'verbose_name': _('publish'),
    'view_permissions_required': ['publish'],
    'view_url_registration_required': False,
})

UNPUBLISH_ACTION = ('unpublish', {
    'verbose_name': _('unpublish'),
    'view_permissions_required': ['unpublish'],
    'view_url_registration_required': False,
})

VIEW_REVISIONS_ACTION = ('revisions_index', {
    'verbose_name': _('view revisions'),
    'view_permissions_required': ['edit'],
    'view_url_registration_required': False,
})

DEFAULT_PAGE_MODEL_ACTIONS = [INDEX_ACTION, CREATE_ACTION, INSPECT_ACTION,
                              EDIT_ACTION, DELETE_ACTION, CHOOSE_PARENT_ACTION,
                              ADD_SUBPAGE_ACTION, PREVIEW_ACTION, COPY_ACTION,
                              MOVE_ACTION, VIEW_DRAFT_ACTION, PUBLISH_ACTION,
                              UNPUBLISH_ACTION, VIEW_REVISIONS_ACTION]
