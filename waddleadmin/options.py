from __future__ import unicode_literals

import re

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin as WagtailModelAdmin

from .actions import ( # noqa
    ModelAction, DEFAULT_MODEL_ACTIONS, DEFAULT_PAGE_MODEL_ACTIONS
)
from .helpers.permission import PermissionHelper, PagePermissionHelper
from .helpers.url import AdminURLHelper, PageAdminURLHelper
from .helpers.button import GenericButtonHelper


class ModelAdmin(WagtailModelAdmin):
    model_actions = None
    custom_model_actions = {}
    index_view_button_names = None
    inspect_view_button_names = None
    default_button_css_classes = ['button']
    create_button_css_classes = ['bicolor', 'icon', 'icon-plus']
    delete_button_css_classes = ['no']

    def __init__(self, parent=None):
        super(ModelAdmin, self).__init__(parent)

        # Just these extra attributes for reference
        self.model_name_singular = force_text(self.opts.verbose_name)
        self.model_name_plural = force_text(self.opts.verbose_name_plural)

        # Create ModelAction instances from definitions and store in private
        # dict for easy access
        self._actions = {}
        for codename, action_kwargs in self.get_action_definitions():
            action = ModelAction(codename, self, **action_kwargs)
            self._actions[codename] = action

    def get_permission_helper_class(self):
        # No changes here, really! This is just to load our new versions of
        # the two helper classes
        if self.permission_helper_class:
            return self.permission_helper_class
        if self.is_pagemodel:
            return PagePermissionHelper
        return PermissionHelper

    def get_url_helper_class(self):
        # No changes here, really! This is just to load our new versions of
        # the two helper classes
        if self.url_helper_class:
            return self.url_helper_class
        if self.is_pagemodel:
            return PageAdminURLHelper
        return AdminURLHelper

    def get_button_helper_class(self):
        # Replaces the current two ButtonHelper classes with the new
        # GenericButtonHelper one
        if self.button_helper_class:
            return self.button_helper_class
        return GenericButtonHelper

    def get_action_definitions(self):
        # If self.model_actions is explicity set, return that only
        if self.model_actions:
            return self.model_actions

        # Start with default actions
        if self.is_pagemodel:
            model_actions = DEFAULT_PAGE_MODEL_ACTIONS
        else:
            model_actions = DEFAULT_MODEL_ACTIONS

        # If no custom actions are defined, just return the defaults
        if not self.custom_model_actions:
            return model_actions

        # Custom actions were defined. First, ensure custom action codenames
        # are all valid
        valid_codename_pattern = re.compile("^([a-z_]+)+$")
        for codename in self.custom_model_actions.keys():
            if not valid_codename_pattern.match(codename):
                raise ImproperlyConfigured(
                    "You're trying to register an action with an invalid "
                    "codename '%s' on your '%s' class. Action codenames must "
                    "contain lower case ascii letters and underscores only" % (
                        codename, self.__class__.__name__
                    )
                )

        # Combine default and custom actions
        model_actions.update(self.custom_model_actions)
        return model_actions

    def get_action(self, codename):
        self._actions.get(codename)

    def get_admin_urls_for_registration(self):
        return [
            action.url for codename, action in self.actions.items()
            if action.view_url_registration_required
        ]

    def get_index_view_button_names(self, request):
        """
        Return a list or tuple of 'codenames' for buttons that should be
        displayed in the InspectView for instances of `self.model`, in the
        order that those buttons should be displayed. Values can also be a
        tuple in the format (label, codename_list_for_dropdown) to create a
        dropdown menu
        """
        if self.index_view_button_names is not None:
            return self.index_view_button_names
        if self.is_pagemodel:
            return (
                'inspect', 'edit', 'view_live', (
                    _('More'), ('copy', 'delete', 'unpublish')
                ),
            )
        return ('inspect', 'edit', 'delete')

    def get_inspect_view_button_names(self, request):
        """
        Return a list or tuple of 'codenames' for buttons that should be
        displayed in the InspectView for instances of `self.model`, in the
        order that those buttons should be displayed. Only flat lists are
        supported here
        """
        if self.inspect_view_button_names is not None:
            return self.inspect_view_button_names
        if self.is_pagemodel:
            return ('edit', 'copy', 'delete', 'unpublish')
        return ('edit', 'delete')

    def get_button_url_for_action(self, codename, obj):
        """
        Return a URL to be used as the `href` attribute for buttons with action
        `codename` for `obj` (an instance of `self.model` or `None`)
        """
        url = self.get_action(codename).get_button_url(obj)
        return url or self.url_helper.get_action_url_for_obj(codename, obj)

    def get_button_label_for_action(self, codename, obj):
        """
        Return a string to be used as the `label` text for buttons with action
        `codename` for `obj` (an instance of `self.model` or `None`)
        """
        action = self.get_action(codename)
        label = action.get_button_label(obj)
        if label:
            return label
        if codename == 'create':
            return _('Add %s') % self.model_verbose_name
        return action.verbose_name.capitalize()

    def get_button_title_for_action(self, codename, obj):
        """
        Return a string to be used as the `title` text for buttons with action
        `codename` for `obj` (an instance of `self.model` or `None`)
        """
        action = self.get_action(codename)
        title = action.get_button_title(obj)
        if title:
            return title
        if codename == 'create':
            return _('Create a new %s') % self.model_verbose_name
        if codename == 'dropdown':
            return _("View more options for '%s'") % obj
        if codename == 'view_draft':
            return _("Preview draft version of '%s'") % obj
        if codename == 'view_live':
            return _("View live version of '%s'") % obj
        if codename == 'revisions_index':
            return _("View revision history for '%s'") % obj
        if codename == 'add_subpage':
            return _("Add child page to '%s'") % obj
        return _("%(action)s %(model_name)s '%(obj_representation)s'") % {
            'action': action.verbose_name.capitalize(),
            'model_name': self.model_verbose_name,
            'obj_representation': obj,
        }

    def get_button_classes_for_action(self, codename, obj):
        """
        Returns a set of css classes to be added to buttons with action
        `codename` for `obj` (an instance of `self.model` or `None`)
        """
        classes = set(self.default_button_css_classes)
        classes.extend(
            self.get_action(codename).get_button_extra_classes()
        )
        return classes

    def get_permission_required_for_action(self, codename):
        return self.get_action(codename).permission_required
