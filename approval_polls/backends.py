import logging

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from passageidentity import Passage


class PassageAuth(BaseBackend):
    """
    Class to authenticate the user based on the given username or Email ID.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        psg = Passage(settings.PASSAGE_APP_ID)
        user = psg.validateJwt(request)
        logging.info(f"User: {user}")
        return user
