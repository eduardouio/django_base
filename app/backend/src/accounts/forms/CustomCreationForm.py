from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUserModel


class CustomCreationForm(UserCreationForm):
    class Meta:
        model = CustomUserModel
        fields = ('__all__')