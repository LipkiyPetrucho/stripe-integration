import os

import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from payments.models import Item

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def buy_item(request, id):
    item = get_object_or_404(Item, id=id)
    success_url = request.build_absolute_uri(reverse("payment:completed"))
    cancel_url = request.build_absolute_uri(reverse("payment:canceled"))
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": item.currency,
                    "product_data": {
                        "name": item.name,
                    },
                    "unit_amount": int(item.price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return JsonResponse({"sessionId": session.id})


def item_detail(request, id):
    item = get_object_or_404(Item, id=id)
    context = {
        "item": item,
        "stripe_publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
    }
    return render(request, "payments/item_detail.html", context)


def payment_completed(request):
    return render(request, "payment/completed.html")


def payment_canceled(request):
    return render(request, "payment/canceled.html")
