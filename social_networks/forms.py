from django.forms import ModelForm
from django import forms
from .models import Entry


class CreateEntryForm(ModelForm):
    """
    Form for creating new entry.
    """

    class Meta:
        model = Entry
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={}),
            'text': forms.Textarea(attrs={})
        }