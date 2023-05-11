import sys

from django.urls import reverse
from django.http import HttpResponseRedirect
from social import exceptions as social_exceptions
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, social_exceptions.AuthCanceled):
            return HttpResponseRedirect(reverse("auth_login"))
        else:
            raise Exception(None, sys.exc_info()[2])  # noqa:W602
