from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from payapp.models import Account
import requests
from decimal import Decimal

BASELINE_AMOUNT = 750



def convert_currency(from_currency, to_currency, amount):
    url = f"http://127.0.0.1:8000/pay/conversion/{from_currency}/{to_currency}/{amount}/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return Decimal(result['converted_amount'])
        else:
            raise Exception("Conversion failed")
    except:
        raise Exception("Currency conversion error")


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            currency = form.cleaned_data.get('currency')
            try:
                converted = convert_currency('GBP', currency, BASELINE_AMOUNT)
            except Exception:
                converted = Decimal('750.00')  # fallback
            Account.objects.create(user=user, currency=currency, balance=converted)

            login(request, user)
            return redirect('account')
    else:
        form = SignUpForm()
    return render(request, 'register/register.html', {'form': form})
