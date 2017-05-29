from approval_polls.models import Subscription
from approval_frame.mailchimp_api import get_mailchimp_api

def run():
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
