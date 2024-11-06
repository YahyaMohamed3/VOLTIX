# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "company_name", "date_of_birth")

class CustomLoginForm(AuthenticationForm):
    email = forms.CharField(label="email")
    password = forms.CharField(label="Password" , widget=forms.PasswordInput)