import json
import os
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from cart.forms import CartAddItemForm
from orders.models import Order
from payments.models import Item

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")


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
        stripe_tax_ids = []
        if order.tax.exists():
            for tax in order.tax.all():
                stripe_tax = stripe.TaxRate.create(
                    display_name=tax.name,
                    inclusive=True,
                    percentage=tax.rate,
                )
                stripe_tax_ids.append(stripe_tax.id)

        # Обрабатываем каждую позицию в заказе
        for order_item in order.items.all():
            item = order_item.item
            price_in_rubles = order_item.convert_item_price()
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(price_in_rubles * Decimal("100")),
                        "currency": "rub",
                        "product_data": {
                            "name": item.name,
                        },
                    },
                    "quantity": order_item.quantity,
                    "tax_rates": stripe_tax_ids,
                }
            )
        # купон Stripe
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code, percent_off=order.discount, duration="once"
            )
            session_data["discounts"] = [{"coupon": stripe_coupon.id}]
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    else:
        return render(request, "payments/item/process.html", locals())


def buy_order_intent(request):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        total_amount = int(order.get_total_cost() * Decimal("100"))

        stripe_tax_ids = []
        if order.tax.exists():
            for tax in order.tax.all():
                stripe_tax = stripe.TaxRate.create(
                    display_name=tax.name,
                    inclusive=True,
                    percentage=tax.rate,
                )
                stripe_tax_ids.append(stripe_tax.id)

        items_data = []
        for order_item in order.items.all():
            item = order_item.item
            price_in_rubles = order_item.convert_item_price()
            items_data.append(
                {
                    "price_data": {
                        "unit_amount": int(price_in_rubles * Decimal("100")),
                        "currency": "rub",
                        "product_data": {
                            "name": item.name,
                        },
                    },
                    "quantity": order_item.quantity,
                    "tax_rates": stripe_tax_ids,
                }
            )

        # Обрабатываем каждую позицию в заказе
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency="rub",
            metadata={
                "order_id": order.id,
                "order_items": json.dumps(items_data),
            },
        )
        completed_url = request.build_absolute_uri(reverse("payment:completed"))
        context = {
            "client_secret": intent.client_secret,
            "order": order,
            "stripe_tax_ids": stripe_tax_ids,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
            "completed_url": completed_url,
        }
        return render(request, "payments/item/process_payment.html", context)
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
        "stripe_publishable_key": stripe_publishable_key,
    }
    return render(request, "payments/item/item_detail.html", context)


def payment_completed(request):
    return render(request, "payments/completed.html")


def payment_canceled(request):
    return render(request, "payments/canceled.html")
