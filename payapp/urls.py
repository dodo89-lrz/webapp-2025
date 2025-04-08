from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.account_view, name='account'),
    path('send/', views.send_payment, name='send_payment'),
    path('request/', views.request_payment, name='request_payment'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('payment_request/<int:request_id>/<str:action>/', views.process_payment_request, name='process_payment_request'),
    path('conversion/<str:currency1>/<str:currency2>/<str:amount>/', views.currency_conversion, name='conversion'),
]
