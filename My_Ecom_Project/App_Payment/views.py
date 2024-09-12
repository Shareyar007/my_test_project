from django.shortcuts import render, HttpResponsePermanentRedirect, redirect
from django.contrib import messages
#models and forms
from App_Order.models import Order
from App_Payment.forms import BillingAddress
from App_Payment.forms import BillingForm

from django.contrib.auth.decorators import login_required

#for payment
import requests
#from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket
# Create your views here.
@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == 'POST':
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.success(request, f'Address saved')
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    print(order_qs)
    order_items = order_qs[0].orderitems.all()
    print(order_items)
    order_total = order_qs[0].get_totals()
    print(order_total)
    return render(request, 'App_Payment/checkout.html', context={'form':form, 'order_items':order_items, 'order_total':order_total, 'saved_address': saved_address})

@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    if not saved_address[0].is_fully_filled():
        messages.info(request, f'Please complete shipping address')
        return redirect('App_Payment:checkout')
    if not request.user.profile.is_fully_filled():
        messages.info(request, f"Please complete profile details")
        return redirect('App_Login:profile')
    
    store_id='goose6630dd7d8607a'
    API_key='goose6630dd7d8607a@ssl'
    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id, sslc_store_pass=API_key)
    
    mypayment.set_urls(success_url='example.com/success', fail_url='example.com/failed', cancel_url='example.com/cancel', ipn_url='example.com/payment_notification')

    return render(request, "App_Payment/payment.html", content={})


@login_required
def complete(request):
    render(request, 'App_Payment/complete.html', context={})