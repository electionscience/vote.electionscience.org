from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from forms import NewUsernameForm
from forms import RegistrationFormCustom
from registration.backends.default.views import RegistrationView

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
