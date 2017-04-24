import mailchimp
from django.conf import settings
from approval_polls.models import Subscription

def get_mailchimp_api():
    if settings.MAILCHIMP_API_KEY:
        key = settings.MAILCHIMP_API_KEY
    else:
        key = '00000000000000000000000000000000-us1'
    return mailchimp.Mailchimp(key)


def update_subscription(subscription_preference, email, zipcode):
    try:
        m = get_mailchimp_api()
        lists = m.lists.list()
        list_id = lists['data'][0]['id']
        errors = []
        if subscription_preference:
            m.lists.subscribe(list_id, {'email': email}, {'MMERGE3': zipcode})
        else:
            m.lists.unsubscribe(list_id, {'email': email}, {'MMERGE3': zipcode})
    except mailchimp.ListAlreadySubscribedError: 
        errors.append('newslettercheckbox')
        errors.append('That email is already subscribed to the list')
    except mailchimp.Error, e:
        errors.append('newslettercheckbox') 
        errors.append(e)
    return errors

