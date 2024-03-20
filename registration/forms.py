from django import forms
from django.contrib.auth.forms import UserCreationForm

from sustainability.models import Userprofile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150, help_text='Enter a valid email address.')

    class Meta:
        model = Userprofile
        fields = ['username', 'email', 'password1', 'password2']
