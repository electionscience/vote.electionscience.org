__author__ = 'sparky'
from django import forms
from approval_polls.models import Poll


class PollUpdateForm(forms.ModelForm):
    class Meta:
        model = Poll
        exclude = ('pub_date', 'user', )

    question = forms.CharField(label='Question',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
                               # We specify the widget so we can bootstrapify the class
    open_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    close_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))