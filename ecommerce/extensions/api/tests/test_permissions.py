from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate

from ecommerce.extensions.api.permissions import CanActForUser, IsSuperUser
from ecommerce.tests.testcases import TestCase


class PermissionsTestMixin(object):
    def get_request(self, user=None, data=None):
        request = APIRequestFactory().post('/', data)

        if user:
            force_authenticate(request, user=user)

        return Request(request)


class CanActForUserTests(PermissionsTestMixin, TestCase):
    permissions_class = CanActForUser()

    def test_has_permission_no_data(self):
        """ If no username is supplied with the request data, return False. """
        request = self.get_request()
        self.assertFalse(self.permissions_class.has_permission(request, None))

    def test_has_permission_superuser(self):
        """ Return True if request.user is a superuser. """
        user = self.create_user(is_superuser=True)

        # Data is required, even if you're a superuser.
        request = self.get_request(user=user)
        self.assertFalse(self.permissions_class.has_permission(request, None))

        # Superusers can create their own refunds
        request = self.get_request(user=user, data={'username': user.username})
        self.assertTrue(self.permissions_class.has_permission(request, None))

        # Superusers can create refunds for other users
        request = self.get_request(user=user, data={'username': 'other_guy'})
        self.assertTrue(self.permissions_class.has_permission(request, None))

    def test_has_permission_same_user(self):
        """ If the request.data['username'] matches request.user, return True. """
        user = self.create_user()

        # Normal users can create their own refunds
        request = self.get_request(user=user, data={'username': user.username})
        self.assertTrue(self.permissions_class.has_permission(request, None))

        # Normal users CANNOT create refunds for other users
        request = self.get_request(user=user, data={'username': 'other_guy'})
        self.assertFalse(self.permissions_class.has_permission(request, None))


class IsSuperUserTests(PermissionsTestMixin, TestCase):
    permissions_class = IsSuperUser()

    def test_has_permission_without_user(self):
        """ The method should return False if the request is not authenticated. """
        request = self.get_request()
        self.assertFalse(self.permissions_class.has_permission(request, None))

    def test_has_permission_with_regular_user(self):
        """ The method should return False for non-superusers. """
        user = self.create_user()
        request = self.get_request(user)
        self.assertFalse(self.permissions_class.has_permission(request, None))

    def test_has_permission_with_superuser(self):
        """ The method should return True for superusers. """
        user = self.create_user(is_superuser=True)
        request = self.get_request(user)
        self.assertTrue(self.permissions_class.has_permission(request, None))
