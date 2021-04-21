from django.test import TestCase
from tokenlib.errors import InvalidSignatureError

from polls.exceptions import UnknownUserError
from polls.models import User
from polls.services.system_service import SystemService
from polls.services.user_service import UserService


class SystemServiceTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        UserService().register_new_user('Test user', '1234', 'test@gmail.com', 'country name', '')

    def setUp(self):
        self.user = User.objects(username='Test user').first()
        UserService().login(self.user.username, self.user.password)

    def test_token_invalid_signature_error(self):
        with self.assertRaises(InvalidSignatureError):
            SystemService.verify_token(self.user.id, 'random token')

    def test_token_unknown_user_error(self):
        with self.assertRaises(UnknownUserError):
            SystemService.verify_token('604cb3cd6a900b4b4f95091d', self.user.token)

    def test_correct_token(self):
        self.user.reload()
        self.assertTrue(SystemService.verify_token(self.user.id, self.user.token))

    def tearDown(self):
        UserService().logout(self.user.id)

    @classmethod
    def tearDownClass(cls):
        user = User.objects(username='Test user').first()
        UserService().delete_user_account(user.id, user.password)
