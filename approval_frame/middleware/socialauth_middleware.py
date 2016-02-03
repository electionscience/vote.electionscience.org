from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social import exceptions as social_exceptions
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, social_exceptions.AuthCanceled):
            return HttpResponseRedirect(reverse('auth_login'))
        else:
            raise exception
