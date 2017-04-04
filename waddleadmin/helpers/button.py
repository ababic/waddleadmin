from __future__ import absolute_import, unicode_literals

from django.utils.six import string_types

from wagtail.wagtailadmin.widgets import Button
from ..widgets import ActionButton, DropdownMenuButton


class GenericButtonHelper(object):

    button_class = ActionButton
    dropdown_button_class = DropdownMenuButton

    @classmethod
    def modify_button_css_classes(cls, button, add, remove):
        button.classes.difference_update(remove)
        button.classes.update(add)

    def __init__(self, request, model_admin):
        self.request = request
        self.model_admin = model_admin
        self.permission_helper = model_admin.permission_helper

    def get_button_kwargs_for_action(self, codename, obj=None):
        """
        Attempt to find a method or attribute to that will give us the values
        needed to define a button for action `codename` (potentially for a
        specific `obj`)
        """
        attribute_name = '%s_button_kwargs' % codename
        if hasattr(self.model_admin, attribute_name):
            attribute = getattr(self.model_admin, attribute_name)
        elif hasattr(self, attribute_name):
            attribute = getattr(self, attribute_name)
        else:
            # If no method was found, build our own dictionary
            return self.build_button_kwargs_for_action(codename, obj)

        if not callable(attribute):
            return attribute
        try:
            # Try to call the method with the standard `request` / `obj` args
            return attribute(request=self.request, obj=obj)
        except TypeError:
            # Some button definition methods don't take `obj`
            return attribute(request=self.request)
        return attribute()

    def build_button_kwargs_for_action(self, codename, obj=None):
        """
        Create a dictionary of arguments that can be used to create a button
        for action `codename` for `obj` in the event that no specifically named
        button is defined to do the same thing
        """
        ma = self.model_admin

        # With the exception of 'permissions_required', these values
        # will be used as init kwargs to create a `self.button_class` instance
        return {
            'permissions_required': ma.get_permission_required_for_action(codename),
            'url': ma.get_button_url_for_action(codename, obj),
            'label': ma.get_button_label_for_action(codename, obj),
            'title': ma.get_button_title_for_action(codename, obj),
            'classes': ma.get_button_css_classes_for_action(codename, obj),
        }

    def create_button_instance_from_kwargs(self, obj, **button_kwargs):
        # Note: 'permissions_required' is popped from button_kwargs, and
        # so won't be passed as an init kwarg to `self.button_class`
        perms_required = button_kwargs.pop('permissions_required', [])
        if perms_required:
            # If perms_required is a single string, make it into a tuple
            if isinstance(perms_required, string_types):
                perms_required = (perms_required, )
            # Return `None` is the user doesn't have all necessary permissions
            if not any(
                self.permission_helper.user_has_permission_for_action(
                    self.request.user, perm, obj
                ) for perm in perms_required
            ):
                return None
        title = button_kwargs.pop('title', '')
        try:
            button_kwargs['attrs']['title'] = title
        except KeyError:
            button_kwargs['attrs'] = {'title': title}
        # Always make 'classes' a set
        button_kwargs['classes'] = set(button_kwargs.get('classes', []))
        return self.button_class(**button_kwargs)

    def get_button_set_for_obj(self, obj, codename_list, classes_add=(),
                               classes_remove=()):
        button_definitions = []
        buttons = []

        for val in codename_list:
            if isinstance(val, tuple):
                items = self.get_button_set_for_obj(obj, val[1])
                title = self.model_admin.get_button_title_for_action(
                    'dropdown', obj
                )
                button_definitions.append(self.dropdown_button_class(
                    label=val[0], items=items, attrs={'title': title}
                ))
            else:
                button_definitions.append(
                    self.get_button_kwargs_for_action(val, obj)
                )

        for definition in button_definitions:
            # `definition` could be a `Button` instance
            if isinstance(definition, Button) and definition.show:
                buttons.append(definition)
            elif definition:
                # `definition` is a dict of init kwargs
                button = self.create_button_instance_from_kwargs(
                    obj, **definition
                )
                if button:
                    # `button` could be `None` if, for example, the user was
                    # found to have insufficient permissions
                    self.modify_button_css_classes(
                        button, classes_add, classes_remove
                    )
                    buttons.append(button)
        return buttons

    def get_button(self, codename, obj=None, classes_add=(), classes_remove=()):
        """If appropriate, return a single button instance for action
        `codename`, potentially for a specific `obj`. Otherwise, return `None`
        """
        button_kwargs = self.get_button_kwargs_for_action(codename, obj)
        if not button_kwargs:
            return None
        # `button_kwargs` might be a `Button` instance
        if isinstance(button_kwargs, Button) and button_kwargs.show:
            return button_kwargs
        # `button_kwargs should be a dict
        button = self.create_button_instance_from_kwargs(obj, **button_kwargs)
        if button is not None:
            # `button` could be `None` if, for example, the user was found to
            # have insufficient permissions
            self.modify_button_css_classes(button, classes_add, classes_remove)
        return button

    def inspect_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defnining an
        'inspect' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not self.model_admin.inspect_view_enabled:
            # Prevent the button from appearing if the view is not enabled
            return None
        return self.build_button_kwargs_for_action('inspect', obj)

    def unpublish_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defining an
        'unpublish' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not getattr(obj, 'live', False):
            # Prevent the button from appearing if obj isn't 'live'
            return None
        return self.build_button_kwargs_for_action('unpublish', obj)

    def view_draft_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defnining a
        'view draft' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not getattr(obj, 'has_unpublished_changes', False):
            # Prevent the button from appearing if there is no draft to view
            return None
        return self.build_button_kwargs_for_action('view_draft', obj)

    def view_live_button_kwargs(self, request, obj):
        """If appropriate, return a dict of arguments for defnining a
        'view live' button for `obj`. Otherwise, return `None` to prevent the
        creation of a button"""
        if not getattr(obj, 'live', False):
            # Prevent the button from appearing if obj isn't live
            return None
        ma = self.model_admin
        # This particular button doesn't fit the usual pattern, so just define
        # the dict here instead of deferring to `build_button_kwargs_for_action`
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
