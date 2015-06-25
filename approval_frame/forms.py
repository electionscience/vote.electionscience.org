from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import PasswordResetForm

class RegistrationFormCustom(RegistrationFormUniqueEmail):
    """
    This class includes registration form related, application-
    specific customizations.

    """
    # Overriden to disallow '@' in the username during registration.
    username = forms.RegexField(regex=r'^[\w.+-]+$',
        max_length=30,
        label=_("Username"),
        error_messages={'invalid': _("This value may contain only letters, "
            + "numbers and ./+/-/_ characters.")}
    )

class PasswordResetFormCustom(PasswordResetForm):
    """
    This class includes password reset form related, application-
    specific customizations.

    """
    def clean_email(self):
        # Make sure that the email address entered is associated with
        # a registered, active user.
        email = self.cleaned_data["email"]
        try:
            next(self.get_users(email))
        except StopIteration:
            raise forms.ValidationError(
                _("This email address is not registered with us or " + 
                "belongs to an account that hasn't been activated.")
            )
        return email
