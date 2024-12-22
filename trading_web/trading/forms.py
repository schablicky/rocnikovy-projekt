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
        fields = ['apikey', 'metaid']
        widgets = {
            'apikey': forms.TextInput(attrs={'class': 'form-control'}),
            'metaid': forms.TextInput(attrs={'class': 'form-control'}),
        }

