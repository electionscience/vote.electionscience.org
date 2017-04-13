from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from forms import NewUsernameForm
from forms import RegistrationFormCustom
from forms import ManageSubscriptionsForm
from registration.backends.default.views import RegistrationView
from approval_polls.models import Subscription
from mailchimp_api import get_mailchimp_api
import mailchimp


@login_required
def changeUsername(request):
    if request.method == 'POST':

        form = NewUsernameForm(request.POST)

        if form.is_valid():
            newusername = form.cleaned_data['new_username']
            owner = request.user
            owner.username = newusername
            owner.save()
            return HttpResponseRedirect(
                '/accounts/username/change/done/'
                )
    else:
        form = NewUsernameForm()

    return render(
        request,
        'registration/username_change_form.html',
        {'form': form}
    )


@login_required
def changeUsernameDone(request):
    return render(
        request,
        'registration/username_change_done.html',
        {'new_username': request.user}
    )

@login_required
def manageSubscriptions(request):
    current_user = request.user
    if request.method == 'POST':
        form = ManageSubscriptionsForm(request.POST)
        if form.is_valid():
            zipcode = form.cleaned_data.get('zipcode')
            newslettercheckbox = form.cleaned_data.get('newslettercheckbox') 
            if current_user.subscription_set.count() > 0:
                if not newslettercheckbox and not zipcode:
                    current_user.subscription_set.first().delete()
            else:
                subscr = Subscription(user=current_user, zipcode=zipcode)
                subscr.save() 
            return HttpResponseRedirect(
                '/accounts/subscription/change/done/'
                )
    else:
        if current_user.subscription_set.count() > 0:
            subscr = current_user.subscription_set.first()
            form = ManageSubscriptionsForm(initial={'user':request.user,'zipcode':subscr.zipcode}) 
            boxchecked = True
        else:
            form = ManageSubscriptionsForm()
            boxchecked = False

        return render(
            request,
            'registration/subscription_preferences.html',
            {'form': form,'boxchecked':boxchecked}
        )     


@login_required
def manageSubscriptionsDone(request):
    return render(
        request,
        'registration/subscription_change_done.html',
        {'new_username': request.user}
    )

class CustomRegistrationView(RegistrationView):
    form_class = RegistrationFormCustom

    def form_valid(self, request, form):
        try:
            m = get_mailchimp_api()
            lists = m.lists.list()
            list_id = lists['data'][0]['id']
            if 'newslettercheckbox' in request.POST:
                m.lists.subscribe(list_id, {'email': request.POST['email']}, {'MMERGE3': request.POST['zipcode']})
            return super(CustomRegistrationView, self).form_valid(request, form)
        except mailchimp.ListAlreadySubscribedError:
            form.add_error('newslettercheckbox', 'That email is already subscribed to the list')
            return render(request, 'registration/registration_form.html', {'form': form})
        except mailchimp.Error, e:
            form.add_error('newslettercheckbox', e)
            return render(request, 'registration/registration_form.html', {'form': form})
