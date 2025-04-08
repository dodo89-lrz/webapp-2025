from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

CURRENCY_CHOICES = [
    ('GBP', 'British Pound'),
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
]

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'currency', 'password1', 'password2')
