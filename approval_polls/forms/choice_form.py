__author__ = 'sparky'
from django import forms
from approval_polls.models import Choice


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        exclude = ('poll', )

    choice_text = forms.CharField(label='Choice',
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))