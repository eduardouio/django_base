from django import forms
from django.contrib.auth.forms import UserChangeForm
from accounts.models import CustomUserModel


class CustomChangeForm(UserChangeForm):
    class Meta:
        model = CustomUserModel
        fields = ('__all__')