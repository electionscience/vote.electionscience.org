from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class EmailOrUsernameBackend(ModelBackend):
    """
    Class to authenticate the user based on the given username or Email ID.

    """
    def authenticate(self, username=None, password=None):
        try:
            validate_email(username)
            kwargs = {'email': username}
        except ValidationError:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
