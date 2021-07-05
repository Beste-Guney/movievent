from django import forms
from accounts.models import Profile


class FriendForm(forms.Form):

    class Meta:
        fields = ['friends', ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        owner_profile = Profile.objects.get(user=user)
        self.fields['friends'] = forms.ModelChoiceField(queryset=owner_profile.friends.all())
