from __future__ import unicode_literals

from django.utils.functional import cached_propery

from wagtail.contrib.modeladmin.helpers import (
    PermissionHelper as WagtailPermissionHelper,
    PagePermissionHelper as WagtailPagePermissionHelper
)


class PermissionHelper(WagtailPermissionHelper):

    @cached_propery
    def inspect_permission_exists(self):
        perm_codename = self.get_perm_codename('inspect')
        return self.get_all_model_permissions().filter(
            codename__exact=perm_codename).exists()

    def user_can_inspect_obj(self, user, obj):
        if not self.inspect_view_enabled:
            return False
        if not self.inspect_permission_exists:
            return self.user_can_list(user)
        return self.no_method_fallback_check(user, 'inspect', obj)

    def user_has_permission_for_action(self, user, codename, obj):
        """
        Looks for a method on `self` to check whether `user` has sufficient
        permissions to perform an action, identified by `codename`. `codename`
        should be an 'action' codename string (e.g. 'edit' or 'delete'), which
        is used to find a method on the PermissionHelper class that can be
        called with the relevant arguments.

        If such a method exists, call it and return a boolean indicating
        the result of the permission check. If no such method exists, call
        `no_method_fallback_check` to do a standard model-wide django
        permission check.
        """
        object_specific_method_name = 'user_can_%s_obj' % codename
        blanket_method_name = 'user_can_%s' % codename

        if obj and hasattr(self, object_specific_method_name):
            method = getattr(self, object_specific_method_name)
            try:
                return method(user=user, obj=obj)
            except TypeError:
                raise TypeError(
                    "The '%s' method on your '%s' class should accept "
                    "'user' and 'obj' as arguments, with no other "
                    "required arguments" % (
                        object_specific_method_name, self.__class__.__name__,
                    )
                )

        elif hasattr(self, blanket_method_name):
            method = getattr(self, blanket_method_name)
            try:
                return method(user=user)
            except TypeError:
                raise TypeError(
                    "The '%s' method on your '%s' class should accept "
                    "'user' as an argument, with no other required "
                    "arguments" % (
                        blanket_method_name, self.__class__.__name__,
                    )
                )

        return self.no_method_fallback_check(user, codename, obj)

        def no_method_fallback_check(self, user, codename, obj):
            # Resort to a standard django auth model-wide permission check
            # for the provided codename
            perm_codename = self.get_perm_codename(codename)
            return self.user_has_specific_permission(user, perm_codename)


class PagePermissionHelper(WagtailPagePermissionHelper, PermissionHelper):

    def no_method_fallback_check(self, user, codename, obj):
        """
        Model-wide django-auth permission checks aren't applicable to page
        trees, so we deny if a specific method hasn't been defined.
        """
        return False
