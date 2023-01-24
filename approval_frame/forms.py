from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail


class RegistrationFormCustom(RegistrationFormUniqueEmail):
    """
    This class includes registration form related, application-
    specific customizations.

    """
    # Overriden to disallow '@' in the username during registration.
    username = forms.RegexField(
        regex=r'^[\w.+-]+$',
        max_length=30,
        label=_("Username"),
        error_messages={'invalid': _(
            "This value may contain only letters, numbers and ./+/-/_ characters."
        )}
    )

    zipcode = forms.CharField(
        required=False,
        label=_("Zip Code (for newsletter)")
        )

    newslettercheckbox = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(RegistrationFormCustom, self).clean()
        zipcode = cleaned_data.get('zipcode')
        newslettercheckbox = cleaned_data.get('newslettercheckbox')
        if newslettercheckbox:
            if zipcode:
                if len(zipcode) != 5 or not zipcode.isdigit():
                    msg = "Please enter a zip code (5 digits, Non-U.S. : 00000)"
                    self.add_error('zipcode', msg)
            else:
                msg = "This field is required."
                self.add_error('zipcode', msg)


class NewUsernameForm(forms.Form):
    """
    This class includes New Username form related customizations.
    Related to valid values a user can enter in the 'New Username' field.

    """
    new_username = forms.RegexField(
        regex=r'^[\w.+-]+$',
        max_length=30,
        error_messages={'invalid': _(
            "This value may contain only letters, numbers and ./+/-/_ characters."
        )}
    )

    def clean_new_username(self):
        new_username = self.cleaned_data['new_username']
        try:
            User.objects.get(username=new_username)
        except User.DoesNotExist:
            return new_username
        raise forms.ValidationError(
            "A user with that username already exists."
        )


class ManageSubscriptionsForm(forms.Form):
    """
    This form is used to manage user subscriptions
    """
    zipcode = forms.CharField(
        required=False,
        label=_("Zip Code (for newsletter)")
        )

    newslettercheckbox = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(ManageSubscriptionsForm, self).clean()
        zipcode = cleaned_data.get('zipcode')
        newslettercheckbox = cleaned_data.get('newslettercheckbox')
        if newslettercheckbox:
            if zipcode:
                if len(zipcode) != 5 or not zipcode.isdigit():
                    msg = "Please enter a zip code (5 digits, Non-U.S. : 00000)"
                    self.add_error('zipcode', msg)
            else:
                msg = "This field is required."
                self.add_error('zipcode', msg)
