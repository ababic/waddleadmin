from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin as WagtailModelAdmin

from .actions import ( # noqa
    ModelAdminAction, DEFAULT_MODEL_ACTIONS, DEFAULT_PAGE_MODEL_ACTIONS
)
from .helpers import GenericButtonHelper


class ModelAdmin(WagtailModelAdmin):
    model_actions = None
    extra_model_actions = []
    index_view_button_names = None
    inspect_view_button_names = None
    default_button_css_classes = ['button']
    create_button_css_classes = ['bicolor', 'icon', 'icon-plus']
    delete_button_css_classes = ['no']

    def __init__(self, parent=None):
        super(ModelAdmin, self).__init__(parent)
        # Just these extra attributes for reference
        self.model_name = force_text(self.opts.verbose_name)
        self.model_name_plural = force_text(self.opts.verbose_name_plural)
        # Create ModelAdminAction instances from definitions
        self._actions = {}
        for action in self.get_action_definitions():
            codename, kwargs = action
            kwargs.update({'model_admin': self, 'codename': codename})
            self._actions[codename] = ModelAdminAction(**kwargs)

    def get_action_definitions(self):
        if self.model_actions:
            return self.model_actions
        extra = list(self.extra_model_actions)
        if self.is_pagemodel:
            return DEFAULT_PAGE_MODEL_ACTIONS + extra
        return DEFAULT_MODEL_ACTIONS + extra

    def get_action(self, codename):
        self._actions.get(codename)

    def get_actions_for_url_registration(self):
        return {k: v for k, v in self._actions if v.url_registration_required}

    def get_admin_urls_for_registration(self):
        for action in self.get_actions_for_url_registration():
            pass

    def get_button_helper_class(self):
        """
        Returns a ButtonHelper class to help generate buttons for the given
        model.
        """
        if self.button_helper_class:
            return self.button_helper_class
        # Just the new class instead of the old helper classes
        return GenericButtonHelper

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
        url = self.get_action(codename).get_button_url_for_obj(obj)
        return url or self.url_helper.get_action_url_for_obj(codename, obj)

    def get_button_label_for_action(self, codename, obj):
        """
        Return a string to be used as the `label` text for buttons with action
        `codename` for `obj` (an instance of `self.model` or `None`)
        """
        action = self.get_action(codename)
        label = action.get_button_label_for_obj(obj)
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
        title = action.get_button_title_for_obj(obj)
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
            self.get_action(codename).get_button_extra_classes_for_obj()
        )
        return classes
