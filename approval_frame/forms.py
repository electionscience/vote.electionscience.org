from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail

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


class NewUsernameForm(forms.Form):
    """
    This class includes New Username form related customizations.
    Related to valid values a user can enter in the 'New Username' field.

    """
    new_username = forms.RegexField(regex=r'^[\w.+-]+$',
        max_length=30,
        error_messages={'invalid': _("This value may contain only letters, "
            + "numbers and ./+/-/_ characters.")}
    )
    