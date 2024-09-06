import os
from decimal import Decimal

import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from cart.forms import CartAddItemForm
from orders.models import Order
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
                    "unit_amount": int(item.price * Decimal("100")),
                    "currency": item.currency,
                    "product_data": {
                        "name": item.name,
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return JsonResponse({"sessionId": session.id})


def buy_order(request):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        for item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": item.item.currency,
                        "product_data": {
                            "name": item.item.name,
                        },
                    },
                    "quantity": item.quantity,
                }
            )

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    else:
        return render(request, "payments/item/process.html", locals())


def item_list(request):
    items = Item.objects.all()
    context = {"items": items}
    return render(request, "payments/item/item_list.html", context)


def item_detail(request, id):
    item = get_object_or_404(Item, id=id)
    cart_item_form = CartAddItemForm()
    context = {
        "item": item,
        "cart_item_form": cart_item_form,
        "stripe_publishable_key": os.getenv(
            "STRIPE_PUBLISHABLE_KEY"
        ),  # убрать ключ так как он скорее всего не нужен тут.
    }
    return render(request, "payments/item/item_detail.html", context)


def payment_completed(request):
    return render(request, "payment/completed.html")


def payment_canceled(request):
    return render(request, "payment/canceled.html")
