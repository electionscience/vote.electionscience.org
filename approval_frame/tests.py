from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from registration import forms
from approval_frame.forms import RegistrationFormCustom
from approval_frame.forms import PasswordResetFormCustom

class UserLoginTests(TestCase):
    """
    This class tests for user login validations.

    """
    errorString = 'Invalid credentials. Please try again.'
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
    This class tests the custom registration form functionality.

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
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])


class PasswordResetFormCustomTests(TestCase):
    """
    This class tests the custom password reset form functionality.

    """
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('user1', 'user1@example.com',
            'user1Password')
        user.save()

    def test_custom_email_validations(self):
        """
        Test that `PasswordResetFormCustom` enforces that the 
        custom validations on invalid input.

        """ 
        invalid_data_dicts = [
            # Do not allow the application to send an email to an
            # unregistered or inactive user.
            {'data': {'email': 'unregistereduser@somedomain.com',},
             'error': ('email', ["This email address is not registered with " +
                "us or belongs to an account that hasn't been activated."])},]

        for invalid_dict in invalid_data_dicts:
            form = PasswordResetFormCustom(data=invalid_dict['data'])
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

    def test_valid_email(self):
        """
        Test that `PasswordResetFormCustom` allows sending a reset email to a
        registered.

        """
        response = self.client.post('/accounts/password/reset/',
            data={'email': 'user1@example.com'},
            follow=True)
        self.assertContains(response, "We have emailed a link for " +
            "resetting your password", status_code=200)