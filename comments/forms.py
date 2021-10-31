from django import forms

class CommentForm(forms.Form):
  comment = forms.CharField(label="Add new comment", widget=forms.TextInput(attrs={
    "id": 'main_form_comment'}))

class AnswerOnCommentForm(forms.Form):
  comment = forms.CharField(label="Answer")