from __future__ import unicode_literals

from wagtail.contrib.modeladmin.helpers.permission import (
    PermissionHelper as WagtailPermissionHelper,
    PagePermissionHelper as WagtailPagePermissionHelper
)


class PermissionHelper(WagtailPermissionHelper):

    def user_has_permission_for_action(self, user, codename, obj):
        """
        Attempts to find a method on `self` to check whether `user` has
        sufficient permissions to perform an action with codename `codename`.
        If then attempts to call the method and return a boolean value,
        indicating whether the check passed or failed.
        """
        object_specific_method_name = 'user_can_%s_obj' % codename
        blanket_method_name = 'user_can_%s' % codename

        if obj and hasattr(self, object_specific_method_name):
            attr = getattr(self, object_specific_method_name)
            try:
                return attr(user=user, obj=obj)
            except TypeError:
                raise TypeError(
                    "The '%s' method on your '%s' class should accept "
                    "'user' and 'obj' as arguments, with no other "
                    "required arguments" % (
                        object_specific_method_name, self.__class__.__name__,
                    )
                )

        elif hasattr(self, blanket_method_name):
            attr = getattr(self, blanket_method_name)
            try:
                return attr(user=user)
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
        # Deny access unless a method is defined to check for a specific action
        return False
