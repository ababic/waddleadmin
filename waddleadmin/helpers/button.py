from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.widgets import Button
from ..utils.inspection import accepts_kwarg
from ..widgets import ActionButton, DropdownMenuButton


class GenericButtonHelper(object):

    button_class = ActionButton
    dropdown_button_class = DropdownMenuButton
    dropdown_button_title_text = _('View more options')

    @classmethod
    def modify_button_css_classes(cls, button, add, remove):
        button.classes.difference_update(remove)
        button.classes.update(add)

    def __init__(self, request, model_admin):
        self.request = request
        self.model_admin = model_admin
        self.permission_helper = model_admin.permission_helper

    def get_button_kwargs_for_action(self, codename, obj=None,
                                     build_kwargs_if_no_method_found=True):
        """
        Attempt to find a method or attribute that will give us the values
        needed to define a button for action `codename` (potentially for a
        specific `obj`)
        """
        attribute_name = '%s_button_kwargs' % codename
        if hasattr(self.model_admin, attribute_name):
            method = getattr(self.model_admin, attribute_name)
        elif hasattr(self, attribute_name):
            method = getattr(self, attribute_name)
        elif build_kwargs_if_no_method_found:
            # Automatically generate kwargs for button creation
            return self.build_button_kwargs_for_action(codename, obj)
        else:
            # No suitable button definition available
            return

        # Call the method matching attribute_name
        kwargs = {}
        if not callable(method):
            return method
        if accepts_kwarg(method, 'request'):
            kwargs['request'] = self.request
        if accepts_kwarg(method, 'obj'):
            kwargs['obj'] = obj
        return method(**kwargs)

    def build_button_kwargs_for_action(self, codename, obj=None, **kwargs):
        """
        Create a dictionary of arguments that can be used to create a button
        for action `codename` for `obj` in the event that no specifically named
        button is defined to do the same thing
        """
        ma = self.model_admin
        cn = codename

        # With the exception of 'permission_required', these values
        # will be used as init kwargs to create a `self.button_class` instance
        button_kwargs = {
            'url': ma.get_button_url_for_action(cn, obj),
            'label': ma.get_button_label_for_action(cn, obj),
            'title': ma.get_button_title_for_action(cn, obj),
            'classes': ma.get_button_css_classes_for_action(cn, obj),
            'permission_required': ma.get_permission_required_for_action(cn),
        }
        button_kwargs.update(kwargs)
        return button_kwargs

    def create_button_from_button_kwargs(self, button_kwargs, obj=None,
                                         classes_add=(), classes_remove=()):
        if not button_kwargs:
            # A None value or empty dict indicates that this button shouldn't
            # be defined
            return

        # `button_kwargs` should be a dictionary of kwargs for creating a
        # `Button` instance, so let's try that

        # Check that the user has sufficient pemissions for the action
        permission_codename = button_kwargs.pop('permission_required', None)
        if permission_codename and not self.permission_helper.user_can(
            self.request.user, permission_codename, obj
        ):
            return  # The user has insufficient permissions

        # Add title to `attrs` so the Button renders it as `title` attribue
        title = button_kwargs.pop('title', None)
        if title:
            try:
                button_kwargs['attrs']['title'] = title
            except KeyError:
                button_kwargs['attrs'] = {'title': title}

        # Always make 'classes' a set
        button_kwargs['classes'] = set(button_kwargs.get('classes', []))

        # Create an an actual `Button`
        button = self.button_class(**button_kwargs)

        # Modify CSS classes before returning
        self.modify_button_css_classes(button, classes_add, classes_remove)
        return button

    def get_button(self, codename, obj=None, classes_add=(),
                   classes_remove=()):
        """If appropriate, return an individual button instance for action
        `codename`, potentially for a specific `obj`. Otherwise, return `None`
        """
        definition = self.get_button_kwargs_for_action(codename, obj)
        return self.create_button_from_button_kwargs(
            definition, obj, classes_add, classes_remove
        )

    def get_button_set_definitions(self, obj, codename_list):
        for val in codename_list:
            if isinstance(val, tuple):
                label, included_codenames = val
                items = self.get_button_set(obj, included_codenames)
                title = self.dropdown_button_title_text
                yield self.dropdown_button_class(
                    label=label, items=items, attrs={'title': title}
                )
            else:
                definition = self.get_button_kwargs_for_action(val, obj)
                if definition:
                    yield definition

    def get_button_set(self, obj, codename_list, classes_add=(),
                       classes_remove=()):
        for definition in self.get_button_set_definitions(obj, codename_list):
            if isinstance(definition, Button):
                # 'definition' could be a `DropdownMenuButton` or an
                # `ActionButton` instance returned by a custom definition
                # method instead of a dictionary (which is acceptable)
                if definition.show:
                    yield definition
            else:
                button = self.create_button_from_button_kwargs(
                    definition, obj, classes_add, classes_remove
                )
                if button:
                    yield button

    def inspect_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defnining an
        'inspect' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not self.model_admin.inspect_view_enabled:
            return  # button shouldn't be rendered
        return self.build_button_kwargs_for_action('inspect', obj)

    def unpublish_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defining an
        'unpublish' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not getattr(obj, 'live', False):
            return  # button shouldn't be rendered
        return self.build_button_kwargs_for_action('unpublish', obj)

    def view_draft_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defnining a
        'view draft' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not getattr(obj, 'has_unpublished_changes', False):
            return  # button shouldn't be rendered
        return self.build_button_kwargs_for_action('view_draft', obj)

    def view_live_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defnining a
        'view live' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not getattr(obj, 'live', False):
            return  # button shouldn't be rendered

        # This particular button doesn't fit the usual pattern, so just define
        # the dict here instead of using `build_button_kwargs_for_action`
        ma = self.model_admin
        return {
            'url': obj.relative_url(request.site),
            'label': ma.get_button_label_for_action('view_live', obj),
            'title': ma.get_button_title_for_action('view_live', obj),
            'classes': ma.get_button_css_classes_for_action('view_live', obj),
            'attrs': {'target': '_blank'},
        }

    def add_button(self):
        """Added for backwards compatibility only. ModelAdmin should use
        'create' rather than 'add' for consistency"""
        return self.get_button('create')
