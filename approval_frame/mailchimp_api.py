import mailchimp
from django.conf import settings


def get_mailchimp_api():
    if settings.MAILCHIMP_API_KEY:
        key = settings.MAILCHIMP_API_KEY
    else:
        key = '00000000000000000000000000000000-us1'
    return mailchimp.Mailchimp(key)
