__author__ = 'sparky'
from django.utils import timezone
from django import forms
from approval_polls.models import Poll
import ast

class PollUpdateForm(forms.ModelForm):
    class Meta:
        model = Poll
        exclude = ('pub_date', 'user', )
    CHOICES=[('True','Inactive'),
             ('False','Active')]
    question = forms.CharField(label='Question',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
                               # We specify the widget so we can bootstrapify the class
    open_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    close_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    suspended = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

    def clean(self):
        cleaned_data = super(PollUpdateForm, self).clean()
        suspended = cleaned_data.get("suspended")
        close_date = cleaned_data.get("close_date")

        if ast.literal_eval(suspended) is False:
            if close_date < timezone.datetime.date(timezone.now()):
                raise forms.ValidationError(
                    "Your close date is in the past. "
                    "Please update the close date."
                )
