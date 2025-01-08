from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import CustomUser, Message

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2') 

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['apikey', 'metaid', 'theme']
        widgets = {
            'apikey': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
            'metaid': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
            'theme': forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}),
        }

class NewChatForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md p-2'}))