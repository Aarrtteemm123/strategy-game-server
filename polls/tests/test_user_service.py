from django.test import TestCase
from polls.models import User
from polls.services.user_service import UserService

class UserServiceTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        UserService().register_new_user('Test user','1234','test@gmail.com','country name','')

    def setUp(self):
        self.user = User.objects(username='Test user').first()

    def tearDown(self):
        pass

    def test_login(self):
        self.assertEqual(self.user.token, '')
        self.assertFalse(self.user.isAuth)

        UserService().login(self.user.username,self.user.password)
        self.user.reload()

        self.assertNotEqual(self.user.token, '')
        self.assertTrue(self.user.isAuth)

    def test_logout(self):
        self.assertNotEqual(self.user.token, '')
        self.assertTrue(self.user.isAuth)

        UserService().logout(self.user.id)
        self.user.reload()

        self.assertEqual(self.user.token, '')
        self.assertFalse(self.user.isAuth)

    def test_change_password(self):
        new_password = '12345'

        UserService().change_user_data(self.user.id, new_password=new_password)
        self.user.reload()

        self.assertEqual(self.user.password, new_password)

    def test_change_country_name(self):
        new_country_name = 'New country'

        UserService().change_user_data(self.user.id, new_country_name=new_country_name)
        self.user.reload()

        self.assertEqual(self.user.country.name, new_country_name)

    def test_change_country_flag(self):
        new_country_flag = 'Link on new country flag'

        UserService().change_user_data(self.user.id, new_country_flag=new_country_flag)
        self.user.reload()

        self.assertEqual(self.user.country.link_img, new_country_flag)

    @classmethod
    def tearDownClass(cls):
        user = User.objects(username='Test user').first()
        UserService().delete_user_account(user.id,user.password)

