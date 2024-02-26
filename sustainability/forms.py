from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from sustainability.models import PlantOfTheDay


class PlantOfTheDayForm(forms.ModelForm):
    class Meta:
        model = PlantOfTheDay
        fields = ['plant']

class ImageUploadForm(forms.Form):
    image = forms.ImageField(label='Select a plant image to identify')