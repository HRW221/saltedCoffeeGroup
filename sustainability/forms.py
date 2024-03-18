from django import forms
from sustainability.models import PlantOfTheDay
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Userprofile


class PlantOfTheDayForm(forms.ModelForm):
    class Meta:
        model = PlantOfTheDay
        fields = ['plant']


class ImageUploadForm(forms.Form):
    image = forms.ImageField(label='Select a plant image to identify')


class JoinLeaderboardForm(forms.Form):
    leaderboard_code = forms.CharField(label='Leaderboard Code', max_length=6)


class LeaderboardForm(forms.Form):
    leaderboard_name = forms.CharField(label='Leaderboard Name', max_length=100)
    is_public = forms.BooleanField(label='Public', required=False)


class ImageCaptureForm(forms.Form):
    image_data = forms.CharField(widget=forms.HiddenInput())
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

class ChangeDetailsForm(UserChangeForm):
    email = forms.EmailField(max_length=150, help_text='Enter a valid email address.')

    class Meta:
        model = Userprofile
        fields = ['username', 'email', 'password']

class BecomeGameMasterForm(forms.Form):
    code = forms.CharField(max_length=10, required=True)