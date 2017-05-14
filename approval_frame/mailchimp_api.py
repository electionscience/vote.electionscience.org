import mailchimp
from django.conf import settings
from approval_polls.models import Subscription
from registration.signals import user_registered
from django.dispatch import receiver


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

@receiver(user_registered)
def receive_new_user_registered(sender, user, request, **kwargs):
    if 'newslettercheckbox' in request.POST:
        subscr = Subscription(user=user, zipcode=request.POST['zipcode'])
        subscr.save()

def update_user_subscriptions():
    m = get_mailchimp_api()
    lists = m.lists.list()
    list_id = lists['data'][0]['id']
    members = m.lists.members(list_id)['data']
    subscriptions_local = Subscription.objects.all()
    for sub in subscriptions_local:
        user = sub.user
        local_email = user.email 
        user_present = False
        for member in members:
            if member['email'] == local_email:
                user_present = True
                break
        if user_present == False:
            user.subscription_set.first().delete()

if __name__ == "__main__":
    update_user_subscriptions()

