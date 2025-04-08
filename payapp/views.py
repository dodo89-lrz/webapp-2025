from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from register.views import convert_currency
from .models import Account, Transaction, PaymentRequest
from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.http import JsonResponse, HttpResponseBadRequest
from decimal import Decimal, InvalidOperation

CONVERSION_RATES = {
    'GBP': 1,
    'USD': 1.3,
    'EUR': 1.15,
}
@login_required
def account_view(request):
    account = get_object_or_404(Account, user=request.user)
    return render(request, 'payapp/account.html', {'account': account})


@login_required
def send_payment(request):
    error = None
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        try:
            amount = Decimal(request.POST.get('amount'))
        except:
            error = "Invalid amount"
            return render(request, 'payapp/send_payment.html', {'error': error})

        recipient = User.objects.filter(username=recipient_username).first()
        if not recipient:
            error = "Recipient not found"
        else:
            sender_acc = Account.objects.get(user=request.user)
            recipient_acc = Account.objects.get(user=recipient)

            if sender_acc.balance < amount:
                error = "Insufficient balance"
            else:
                try:
                    converted_amount = convert_currency(sender_acc.currency, recipient_acc.currency, amount)
                except Exception:
                    error = "Currency conversion failed"
                    return render(request, 'payapp/send_payment.html', {'error': error})

                with db_transaction.atomic():
                    sender_acc.balance -= amount
                    recipient_acc.balance += converted_amount.quantize(Decimal('0.01'))
                    sender_acc.save()
                    recipient_acc.save()
                    Transaction.objects.create(
                        sender=request.user,
                        recipient=recipient,
                        amount=amount
                    )
                return redirect('transactions')

    return render(request, 'payapp/send_payment.html', {'error': error})


@login_required
def request_payment(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        amount_str = request.POST.get('amount')

        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, TypeError):
            error = "Invalid amount. Please enter a valid number."
            return render(request, 'payapp/request_payment.html', {'error': error})

        target_user = User.objects.filter(username=username).first()
        if not target_user:
            error = "User not found"
        else:
            PaymentRequest.objects.create(
                requester=request.user,
                requestee=target_user,
                amount=amount
            )
            return redirect('transactions')

    return render(request, 'payapp/request_payment.html', {'error': error})


@login_required
def transactions_view(request):
    sent = Transaction.objects.filter(sender=request.user)
    received = Transaction.objects.filter(recipient=request.user)
    requests = PaymentRequest.objects.filter(requestee=request.user, is_accepted=False, is_rejected=False)
    return render(request, 'payapp/transactions.html', {
        'sent_transactions': sent,
        'received_transactions': received,
        'payment_requests': requests,
    })

@login_required
def process_payment_request(request, request_id, action):
    req = get_object_or_404(PaymentRequest, id=request_id, requestee=request.user)

    if action == 'accept':
        sender_acc = Account.objects.get(user=request.user)
        receiver_acc = Account.objects.get(user=req.requester)
        amount = req.amount

        if sender_acc.balance < amount:
            return redirect('transactions')

        try:
            converted_amount = convert_currency(sender_acc.currency, receiver_acc.currency, amount)
        except Exception:
            return redirect('transactions')  # or show error

        with db_transaction.atomic():
            sender_acc.balance -= amount
            receiver_acc.balance += converted_amount.quantize(Decimal('0.01'))
            sender_acc.save()
            receiver_acc.save()
            req.is_accepted = True
            req.save()
            Transaction.objects.create(
                sender=request.user,
                recipient=req.requester,
                amount=amount
            )
    elif action == 'reject':
        req.is_rejected = True
        req.save()

    return redirect('transactions')


# RESTful currency conversion
def currency_conversion(request, currency1, currency2, amount):
    try:
        amount = Decimal(str(amount).strip('/'))

        if currency1 not in CONVERSION_RATES or currency2 not in CONVERSION_RATES:
            return HttpResponseBadRequest("Invalid currency")

        gbp_value = amount / Decimal(CONVERSION_RATES[currency1])
        converted = gbp_value * Decimal(CONVERSION_RATES[currency2])

        return JsonResponse({
            "from": currency1,
            "to": currency2,
            "original_amount": float(amount),
            "converted_amount": float(round(converted, 2))
        })

    except (InvalidOperation, ValueError, TypeError):
        return HttpResponseBadRequest("Invalid amount")