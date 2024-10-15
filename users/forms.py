from django import forms
from django.contrib.auth.forms import AuthenticationForm



class LoginForm(AuthenticationForm):
   
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )