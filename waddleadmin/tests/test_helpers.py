from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from waddleadmin.helpers import PermissionHelper, PagePermissionHelper
from wagtail.wagtailimages.models import Image
from wagtail.tests.testapp.models import EventPage
from wagtail.tests.utils import WagtailTestUtils


class UsersMixin(object):
    fixtures = ['test.json']  # wagtail/tests/testapp/fixtures/test.json

    def setUp(self):
        super(UsersMixin, self).setUp()
        # Create a custom permission
        image_ct = ContentType.objects.get_for_model(Image)
        exterminate_image_permission = Permission.objects.create(
            content_type=image_ct, codename='exterminate_image'
        )
        moderators_group = Group.objects.get(pk=4)
        moderators_group.permissions.add(exterminate_image_permission)

    @staticmethod
    def get_moderator():
        user = get_user_model().objects._create_user(username='moderator', email='moderator@email.com', password='password', is_staff=True, is_superuser=False)
        user.groups.add(Group.objects.get(pk=4))
        return user

    @staticmethod
    def get_editor():
        user = get_user_model().objects._create_user(username='editor', email='editor@email.com', password='password', is_staff=True, is_superuser=False)
        user.groups.add(Group.objects.get(pk=5))
        return user

    @staticmethod
    def get_non_editor():
        user = get_user_model().objects._create_user(username='nobody', email='nobody@email.com', password='password', is_staff=False, is_superuser=False)
        user.groups.add(Group.objects.get(pk=6))
        return user


class TestPermissionHelper(UsersMixin, TestCase, WagtailTestUtils):

    def setUp(self):
        super(TestPermissionHelper, self).setUp()
        self.helper = PermissionHelper(Image)

    def test_user_can_create_images(self):
        self.assertTrue(
            self.helper.user_can(self.create_test_user(), 'create')
        )
        self.assertTrue(
            self.helper.user_can(self.get_moderator(), 'create')
        )
        self.assertTrue(
            self.helper.user_can(self.get_editor(), 'create')
        )
        self.assertFalse(
            self.helper.user_can(self.get_non_editor(), 'create')
        )

    def test_user_can_edit_an_image(self):
        image_obj = Image.objects.get(id=1)
        self.assertTrue(
            self.helper.user_can(self.create_test_user(), 'edit', image_obj)
        )
        self.assertTrue(
            self.helper.user_can(self.get_moderator(), 'edit', image_obj)
        )
        self.assertTrue(
            self.helper.user_can(self.get_editor(), 'edit', image_obj)
        )
        self.assertFalse(
            self.helper.user_can(self.get_non_editor(), 'edit', image_obj)
        )

    def test_user_can_exterminate_images(self):
        # If a permission exists, a superuser will automatically have it
        self.assertTrue(
            self.helper.user_can(self.create_test_user(), 'exterminate')
        )
        # A custom 'exterminate' permission has be created and assigned to the
        # moderator group, so a moderator should be able to 'exterminate' an
        # Image
        self.assertTrue(
            self.helper.user_can(self.get_moderator(), 'exterminate')
        )
        self.assertFalse(
            self.helper.user_can(self.get_editor(), 'exterminate')
        )
        self.assertFalse(
            self.helper.user_can(self.get_non_editor(), 'exterminate')
        )

    def test_user_cannot_transmogrify_images(self):
        # No 'transmogrify' permission exists, so checking this should return
        # False (and raise a warning)
        user = self.create_test_user()
        self.assertFalse(self.helper.user_can(user, 'transmogrify'))


class TestPagePermissionHelper(UsersMixin, TestCase, WagtailTestUtils):

    def setUp(self):
        super(TestPagePermissionHelper, self).setUp()
        self.helper = PagePermissionHelper(EventPage)

    def test_user_can_create_eventpages(self):
        self.assertTrue(
            self.helper.user_can(self.create_test_user(), 'create')
        )
        self.assertTrue(
            self.helper.user_can(self.get_moderator(), 'create')
        )
        # Editors shouldn't be able to create an EventPage
        self.assertFalse(
            self.helper.user_can(self.get_editor(), 'create')
        )
        # Users with no page-related permissions at all certainly shouldn't
        self.assertFalse(
            self.helper.user_can(self.get_non_editor(), 'create')
        )

    def test_user_can_delete_an_eventpage(self):
        christmas = EventPage.objects.get(id=4)
        self.assertTrue(
            self.helper.user_can(self.create_test_user(), 'delete', christmas)
        )
        self.assertTrue(
            self.helper.user_can(self.get_moderator(), 'delete', christmas)
        )
        # Editors shouldn't be able to delete an EventPage
        self.assertFalse(
            self.helper.user_can(self.get_editor(), 'delete', christmas)
        )
        # Users with no page-related permissions at all certainly shouldn't
        self.assertFalse(
            self.helper.user_can(self.get_non_editor(), 'delete', christmas)
        )

    def test_user_cannot_transmogrify_an_eventpage(self):
        user = self.create_test_user()
        christmas = EventPage.objects.get(id=4)
        # The below should result in PagePermissionHelper to looking for a
        # 'can_transmogrify' method on PagePermissionTester, but failing
        # because there is no such method
        self.assertFalse(self.helper.user_can(user, 'transmogrify', christmas))

    def test_user_cannot_move_to_an_eventpage(self):
        user = self.create_test_user()
        christmas = EventPage.objects.get(id=4)
        # The below should result in PagePermissionHelper attempting to call
        # PagePermissionTester.can_move_to(), but failing, because
        # can_move_to() requires an additional 'parent' argument
        self.assertFalse(self.helper.user_can(user, 'move_to', christmas))
