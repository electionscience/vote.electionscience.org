from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail

class RegistrationFormCustom(RegistrationFormUniqueEmail):
    """
    Subclass of `RegistrationFormUniqueEmail` which includes application-
    specific customizations.

    """
    # Overriden to disallow '@' in the username during registration.
    username = forms.RegexField(regex=r'^[\w.+-]+$',
        max_length=30,
        label=_("Username"),
        error_messages={'invalid': _("This value may contain only letters, "
            + "numbers and ./+/-/_ characters.")}
    )
