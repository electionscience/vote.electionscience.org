from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from registration.backends.default.views import RegistrationView

from approval_polls.models import Subscription

from .forms import ManageSubscriptionsForm, NewUsernameForm, RegistrationFormCustom


@login_required
def changeUsername(request):
    if request.method == "POST":
        form = NewUsernameForm(request.POST)

        if form.is_valid():
            newusername = form.cleaned_data["new_username"]
            owner = request.user
            owner.username = newusername
            owner.save()
            return HttpResponseRedirect("/accounts/username/change/done/")
    else:
        form = NewUsernameForm()

    return render(request, "registration/username_change_form.html", {"form": form})


@login_required
def changeUsernameDone(request):
    return render(
        request,
        "registration/username_change_done.html",
        {"new_username": request.user},
    )


@login_required
def manageSubscriptions(request):
    current_user = request.user
    if request.method == "POST":
        form = ManageSubscriptionsForm(request.POST)
        if form.is_valid():
            zipcode = form.cleaned_data.get("zipcode")
            is_subscribed = form.cleaned_data.get("newslettercheckbox")
            if current_user.subscription_set.count() > 0:
                if not is_subscribed:
                    current_user.subscription_set.first().delete()
            else:
                subscr = Subscription(user=current_user, zipcode=zipcode)
                subscr.save()

            return HttpResponseRedirect("/accounts/subscription/change/done/")
        else:
            is_subscribed = False
    else:
        if current_user.subscription_set.count() > 0:
            subscr = current_user.subscription_set.first()
            form = ManageSubscriptionsForm(
                initial={"user": request.user, "zipcode": subscr.zipcode}
            )
            is_subscribed = True
        else:
            form = ManageSubscriptionsForm()
            is_subscribed = False

    return render(
        request,
        "registration/subscription_preferences.html",
        {"form": form, "boxchecked": is_subscribed},
    )


@login_required
def manageSubscriptionsDone(request):
    return render(
        request,
        "registration/subscription_change_done.html",
        {"new_username": request.user},
    )


class CustomRegistrationView(RegistrationView):
    form_class = RegistrationFormCustom

    def form_valid(self, form):
        if "newslettercheckbox" in self.request.POST:
            subscription_errors = update_subscription(
                True, self.request.POST["email"], self.request.POST["zipcode"]
            )
            if len(subscription_errors) == 0:
                return super(CustomRegistrationView, self).form_valid(form)
            else:
                # Assuming `add_error` method accepts (field, error), where 'field' can be None for non-field errors
                form.add_error(None, subscription_errors[0])
                return self.render_to_response(self.get_context_data(form=form))
        return super(CustomRegistrationView, self).form_valid(form)
