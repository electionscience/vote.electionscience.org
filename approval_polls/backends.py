import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = structlog.get_logger(__name__)

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate a user by email.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                logger.debug("User authenticated successfully", user=user)
                return user
        except User.DoesNotExist:
            logger.debug("User does not exist", email=email)
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
