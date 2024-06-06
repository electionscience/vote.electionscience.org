from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import structlog

logger = structlog.get_logger(__name__)

class EmailOrUsernameBackend(ModelBackend):
    """
    Class to authenticate the user based on the given username or Email ID.

    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            validate_email(email)
            kwargs = {"email": email}
        except ValidationError:
            logger.exception("Validation Error on login")
            kwargs = {"email": email}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            logger.info("User does not exist")
            return None
