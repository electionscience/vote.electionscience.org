from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from registration import forms
from approval_frame.forms import RegistrationFormCustom

class UserLoginTests(TestCase):

    errorString = 'Your username and password didn\'t match. Please try again.'
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('user1', 'user1@example.com', 'user1Password')
        user.save()

    def login_user(self, username, password):
        """
        Helper method for user login. Validates both response and login status.

        """
        response = self.client.post('/accounts/login/',
            data={'username':username, 'password':password},
            follow=True
        )
        status = self.client.login(username=username, password=password) 
        return response, status

    def test_invalid_username_password(self):
        """
        Test login with an incorrect username and password combination.

        """
        response, status = self.login_user('user1', 'invalid')
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)

    def test_invalid_email_password(self):
        """
        Test login with an incorrect email and password combination.

        """
        response, status = self.login_user('user1@example.com', 'invalid')
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)


    def test_valid_username_password(self):
        """
        Test login with a correct username and password combination.

        """
        response, status = self.login_user('user1', 'user1Password')
        self.assertNotContains(response, self.errorString, status_code=200)
        self.assertTrue(status)

    def test_valid_email_password(self):
        """
        Test login with a correct email and password combination.

        """
        response, status = self.login_user('user1@example.com', 'user1Password')
        self.assertNotContains(response, self.errorString, status_code=200)
        self.assertTrue(status)

    def test_non_existent_username(self):
        """
        Test login with a non-existent username.
        
        """
        response, status = self.login_user('user2', 'user1Password')
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)

    def test_non_existent_email(self):
        """
        Test login with a non-existent email.

        """
        response, status = self.login_user('user2@example.com', 'user1Password')
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)


class RegistrationFormCustomTests(TestCase):
    """
    Test the custom Registration form class.

    """
    def test_registration_form_custom(self):
        """
        Test that `RegistrationFormCustom` enforces custom username
        constraints during registration.

        """
        invalid_data_dicts = [
            # Username with '@' is invalid.
            {'data': {'username': 'foo@somedomain.com',
                      'email': 'foo@example.com',
                      'password1': 'foo',
                      'password2': 'foo'},
            'error': ('username', ["This value may contain only " +
                       "letters, numbers and ./+/-/_ characters."])},]

        for invalid_dict in invalid_data_dicts:
            form = RegistrationFormCustom(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

