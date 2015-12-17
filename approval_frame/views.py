from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from forms import NewUsernameForm


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
