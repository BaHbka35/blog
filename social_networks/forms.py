from django.forms import ModelForm
from django import forms
from .models import Entry


class CreateEntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={}),
            'text': forms.Textarea(attrs={})
        }

class CommentForm(forms.Form):
  comment = forms.CharField(label="Add comment")

class AnswerOnCommentForm(forms.Form):
  comment = forms.CharField(label="Answer")
  