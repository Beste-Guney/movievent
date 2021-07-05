from django import forms
from django.db.models import fields
from accounts.models import Profile


class ProfileForm(forms.Form):
    bio = forms.CharField(max_length=2000)
    CHOICES = (('action', 'action'), ('romance', 'romance'), ('comedy', 'comedy'), ('horror', 'horror'))
    favourite_style = forms.ChoiceField(choices=CHOICES)

    class Meta:
        fields = ['bio', 'favourite_style']