from __future__ import absolute_import, unicode_literals

import warnings

from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property

from wagtail.wagtailcore.models import Page, UserPagePermissionsProxy


class BasePermissionHelper(object):

    def __init__(self, model, inspect_view_enabled=False):
        self.model = model
        self.opts = model._meta
        self.inspect_view_enabled = inspect_view_enabled

    def user_can(self, user, codename, obj=None):
        """Looks for a method to check whether `user` has sufficient
        permissions to perform the action `codename` (e.g. 'create', 'edit',
        'publish', 'delete') and returns it's result.

        Prefers specifically named methods (e.g. 'user_can_action' ,
        'user_can_action_obj'), but will fall back to
        `do_generic_permission_check` if no such method is found."""

        object_specific_method_name = 'user_can_%s_obj' % codename
        blanket_method_name = 'user_can_%s' % codename

        if obj and hasattr(self, object_specific_method_name):
            method = getattr(self, object_specific_method_name)
            return method(user=user, obj=obj)

        elif hasattr(self, blanket_method_name):
            method = getattr(self, blanket_method_name)
            return method(user=user)

        return self.do_generic_permission_check(user, codename, obj)

    def do_generic_permission_check(self, user, codename, obj=None):
        """
        Returns a boolean indicating whether `user` has permission to
        perform the `codename` action
        """
        raise NotImplementedError(
            "Subclasses of BasePermissionHelper must implement their own "
            "'do_generic_permission_check' method"
        )

    def user_can_create(self, user):
        """
        Returns a boolean to indicate whether `user` is permitted to create new
        instances of `self.model`
        """
        return self.do_generic_permission_check(user, 'create')

    def user_can_edit_obj(self, user, obj):
        """
        Returns a boolean to indicate whether `user` is permitted to 'edit'
        a specific `self.model` instance.
        """
        return self.do_generic_permission_check(user, 'edit', obj)

    def user_can_delete_obj(self, user, obj):
        """
        Returns a boolean to indicate whether `user` is permitted to 'delete'
        a specific `self.model` instance.
        """
        return self.do_generic_permission_check(user, 'delete', obj)

    def user_can_unpublish_obj(self, user, obj):
        """
        Returns a boolean to indicate whether `user` is permitted to
        'unpublish' a specific `self.model` instance.
        """
        return self.do_generic_permission_check(user, 'unpublish', obj)

    def user_can_publish_obj(self, user, obj):
        """
        Returns a boolean to indicate whether `user` is permitted to 'publish'
        a specific `self.model` instance.
        """
        return self.do_generic_permission_check(user, 'publish', obj)

    def user_can_copy_obj(self, user, obj):
        """
        Returns a boolean to indicate whether `user` is permitted to 'copy'
        a specific `self.model` instance.
        """
        return self.do_generic_permission_check(user, 'copy', obj)

    def user_can_list(self, user):
        """
        Returns a boolean to indicate whether `user` is permitted to 'list'
        any instances on `self.model`.
        """
        raise NotImplementedError(
            "Subclasses of BasePermissionHelper must implement their own "
            "'user_can_list' method"
        )

    def user_can_inspect_obj(self, user, obj):
        """
        Returns a boolean to indicate whether `user` is permitted to 'inspect'
        a specific `self.model` instance.
        """
        return self.inspect_view_enabled and self.user_can_list(user)


class PermissionHelper(BasePermissionHelper):
    """
    Provides permission-related helper functions to help determine what a
    user can do with a 'typical' model (where permissions are granted
    model-wide), and to a specific instance of that model.
    """
    def get_all_model_permissions(self):
        """
        Return a queryset of all Permission objects pertaining to the `model`
        specified at initialisation.
        """
        return Permission.objects.filter(
            content_type__app_label=self.opts.app_label,
            content_type__model=self.opts.model_name,
        )

    def get_perm_codename(self, codename):
        """Takes a modeladmin 'action codename' and returns a
        'permission codename' that can be used to query Django auth's
        permission system for the relevant permission.
        """
        if codename == 'edit':
            term = 'change'
        elif codename == 'create':
            term = 'add'
        else:
            term = codename
        return get_permission_codename(term, self.opts)

    @cached_property
    def inspect_permission_exists(self):
        return self.get_all_model_permissions().filter(
            codename__exact=self.get_perm_codename('inspect')
        ).exists()

    def user_has_specific_permission(self, user, perm_codename):
        """
        Combine `perm_codename` with `self.opts.app_label` to call the provided
        Django user's built-in `has_perm` method.
        """
        return user.has_perm("%s.%s" % (self.opts.app_label, perm_codename))

    def do_generic_permission_check(self, user, codename, obj=None):
        """Query django auth's model-wide permission system. Raises a warning
        if the supplied `codename` doesn't match up to an existing
        Permission.
        """
        perm_codename = self.get_perm_codename(codename)
        try:
            return self.user_has_specific_permission(user, perm_codename)
        except Permission.DoesNotExist:
            warnings.warn(
                "No Permission could be found matching action codename "
                "'%s' for model '%s'" % (codename, self.opts.label)
            )
        return False

    def user_has_any_permissions(self, user):
        """
        Return a boolean to indicate whether `user` has any model-wide
        permissions
        """
        for perm in self.get_all_model_permissions().values('codename'):
            if self.user_has_specific_permission(user, perm['codename']):
                return True
        return False

    def user_can_list(self, user):
        """
        Return a boolean to indicate whether `user` is permitted to access the
        list view for self.model
        """
        return self.user_has_any_permissions(user)

    def user_can_inspect_obj(self, user, obj):
        """
        For standard models, developers can add a custom 'inspect' permission
        in order to have granular control over who can 'inspect' objects
        (https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#custom-permissions).
        After migrating, the permission should be applied to the relevant
        groups via the Wagtail CMS in Settings > Groups
        """
        if not self.inspect_view_enabled:
            return False
        if not self.inspect_permission_exists:
            # The default behavior (no specific 'inspect' permission exists)
            return self.user_can_list(user)
        # Respect the custom 'inspect' permission
        return self.do_generic_permission_check(user, 'inspect', obj)


class PagePermissionHelper(BasePermissionHelper):
    """
    Provides permission-related helper functions to help determine what
    a user can do with a model extending Wagtail's Page model. It differs
    from `PermissionHelper`, because model-wide permissions aren't really
    relevant. We generally need to determine permissions on an
    object-specific basis.
    """

    def do_generic_permission_check(self, user, codename, obj=None):
        """If `obj` isn't supplied, return `False`, because model-wide
        permissions don't apply to pages. If `obj` is supplied, query the
        `PagePermissionTester` instance returned by `obj.permissions_for_user`.
        Raises a warning if the supplied `codename` cannot be matched to the
        name of a method or attribute, or the method takes additional arguments
        """
        if not obj:
            # model-wide permission checks for page type models are not
            # supported
            return False

        perms = obj.permissions_for_user(user)
        # Attempt to find a `PagePermissionTester` method / attribute with
        # a relevant name to test with
        attr_name = 'can_%s' % codename
        if hasattr(perms, attr_name):
            attr = getattr(perms, attr_name)
            if not callable(attr):
                return attr
            try:
                return attr()
            except TypeError:
                warnings.warn(
                    "A TypeError was raised by the '%s' method on '%s'. "
                    "It's likely the method takes additional required "
                    "arguments that 'do_generic_permission_check' isn't "
                    "capable of supplying." %
                    (attr_name, type(perms).__name__)
                )
        else:
            warnings.warn(
                "%s has no attribute or method to check for a '%s' "
                "permission" % (type(perms).__name__, codename)
            )
        return False

    def get_valid_parent_pages(self, user):
        """
        Identifies possible parent pages for the current user by first looking
        at allowed_parent_page_models() on self.model to limit options to the
        correct type of page, then checking permissions on those individual
        pages to make sure we have permission to add a subpage to it.
        """
        # Get queryset of pages where this page type can be added
        allowed_parent_page_content_types = list(
            ContentType.objects.get_for_models(
                *self.model.allowed_parent_page_models()
            ).values()
        )
        allowed_parent_pages = Page.objects.filter(
            content_type__in=allowed_parent_page_content_types
        )

        # Get queryset of pages where the user has permission to add subpages
        if user.is_superuser:
            pages_where_user_can_add = Page.objects.all()
        else:
            pages_where_user_can_add = Page.objects.none()
            user_perms = UserPagePermissionsProxy(user)

            for perm in user_perms.permissions.filter(permission_type='add'):
                # user has add permission on any subpage of perm.page
                # (including perm.page itself)
                pages_where_user_can_add |= Page.objects.descendant_of(
                    perm.page, inclusive=True)

        # Combine them
        return allowed_parent_pages & pages_where_user_can_add

    def user_can_list(self, user):
        """
        For models extending Page, permitted actions are determined by
        permissions on individual objects. Rather than check for change
        permissions on every object individually (which would be quite
        resource intensive), we simply always allow the list view to be
        viewed, and limit further functionality when relevant.
        """
        return True

    def user_can_create(self, user):
        """
        For models extending Page, whether or not a page of this type can be
        added somewhere in the tree essentially determines the add permission,
        rather than actual model-wide permissions
        """
        return self.get_valid_parent_pages(user).exists()

    def user_can_copy_obj(self, user, obj):
        parent_page = obj.get_parent()
        return parent_page.permissions_for_user(user).can_publish_subpage()
