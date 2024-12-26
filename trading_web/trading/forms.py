from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'role')

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['apikey', 'metaid', 'theme']
        widgets = {
            'apikey': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
            'metaid': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
            'theme': forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
        }
