from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from approval_frame.forms import RegistrationFormCustom


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
        response = self.client.post(
            '/accounts/login/',
            data={
                'username': username,
                'password': password
            },
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
        invalid_data_dicts = [{
            # Username with '@' is invalid.
            'data': {
                'username': 'foo@somedomain.com',
                'email': 'foo@example.com',
                'password1': 'foo',
                'password2': 'foo'
            },
            'error': (
                'username', ["This value may contain only letters, numbers and ./+/-/_ characters."]
            )
        }, ]

        for invalid_dict in invalid_data_dicts:
            form = RegistrationFormCustom(data=invalid_dict['data'])
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])


class ChangeUsernameTests(TestCase):

    def setUp(self):

        self.client = Client()
        User.objects.create_user(
            'user2',
            'user2ces@gmail.com',
            'password123'
        )
        self.client.login(username='user2', password='password123')

    def test_username_change_error_empty(self):
        '''
        New Username Field is Empty
        '''
        username_data = {'new_username': ''}
        response = self.client.post(
            '/accounts/username/change/',
            username_data,
            follow=True
        )
        html_string = 'This field is required.'
        self.assertContains(response, html_string)

    def test_username_change_illegal_chars_error(self):
        '''
        New Username contains '@'
        '''
        username_data = {'new_username': 'user@1987'}
        response = self.client.post(
            '/accounts/username/change/',
            username_data,
            follow=True
        )
        html_string = 'This value may contain only letters, numbers and ./+/-/_ characters.'
        self.assertContains(response, html_string)

    def test_username_change_maxlen_error(self):
        '''
        New Username is longer than 30 characters
        '''
        username_data = {'new_username': 'kuhhahheriqwemniackolaxcivjkleqwerty'}
        response = self.client.post(
            '/accounts/username/change/',
            username_data,
            follow=True
        )
        html_string = 'Ensure this value has at most 30 characters (it has 36).'
        self.assertContains(response, html_string)

    def test_username_change_already_exists(self):
        '''
        New Username is already registered
        '''
        User.objects.create_user(
            'usertest',
            'usertestces@gmail.com',
            'password123'
        )
        username_data = {'new_username': 'usertest'}
        response = self.client.post(
            '/accounts/username/change/',
            username_data,
            follow=True
        )
        html_string = 'A user with that username already exists.'
        self.assertContains(response, html_string)

    def test_username_change_success(self):
        '''
        Username was successfully changed
        '''
        username_data = {'new_username': 'user1987'}
        response = self.client.post(
            '/accounts/username/change/',
            username_data,
            follow=True
        )
        html_string = 'Your Username was changed to user1987.'
        self.assertContains(response, html_string)


class ChangePasswordTests(TestCase):

    def setUp(self):

        self.client = Client()
        User.objects.create_user(
            'user3',
            'user3ces@gmail.com',
            'password123'
        )
        self.client.login(username='user3', password='password123')

    def test_password_change_error_empty(self):
        '''
        Password Fields are Empty
        '''
        password_data = {
            'old_password': '',
            'new_password1': '',
            'new_password2': ''
        }
        response = self.client.post(
            '/accounts/password/change/',
            password_data,
            follow=True
        )
        html_string = 'This field is required.'
        self.assertContains(response, html_string)

    def test_password_change_old_pass_error(self):
        '''
        Old Password did not match the records
        '''
        password_data = {
            'old_password': 'password1',
            'new_password1': 'password123',
            'new_password2': 'password123'
        }
        response = self.client.post(
            '/accounts/password/change/',
            password_data,
            follow=True
            )
        html_string = 'Your old password was entered incorrectly.'
        self.assertContains(response, html_string)

    def test_password_change_no_match_error(self):
        '''
        New Passwords did not match
        '''
        password_data = {
            'old_password': 'password123',
            'new_password1': 'password123',
            'new_password2': 'password124'
        }
        response = self.client.post(
            '/accounts/password/change/',
            password_data,
            follow=True
            )
        html_string = '<label class="control-label" for="id_new_password2">The two password fields \
        didn&39;t match.</label>'
        self.assertContains(response, html_string, html=True)

    def test_password_change_success(self):
        '''
        Password was successfully changed
        '''
        password_data = {
            'old_password': 'password123',
            'new_password1': 'password1234',
            'new_password2': 'password1234'
        }
        response = self.client.post(
            '/accounts/password/change/',
            password_data,
            follow=True
            )
        html_string = 'Your Password was changed.'
        self.assertContains(response, html_string)
