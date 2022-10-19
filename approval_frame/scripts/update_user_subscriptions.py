import sets

from approval_polls.models import Subscription
from django.contrib.auth.models import User
from approval_frame.mailchimp_api import get_mailchimp_api


def run():
    m = get_mailchimp_api()
    lists = m.lists.list()
    list_id = lists['data'][0]['id']
    members = m.lists.members(list_id)['data']
    subscriptions_local = Subscription.objects.all()
    local_emails = []
    for sub in subscriptions_local:
        user = sub.user
        local_email = user.email
        local_emails.append(local_email)
    mailchimp_emails = [member['email'] for member in members]
    users_to_be_deleted = sets.Set(local_emails) - sets.Set(mailchimp_emails)
    for user_email in users_to_be_deleted:
        u = User.objects.get(email=user_email)
        if u is not None:
            u.subscription_set.first().delete()
