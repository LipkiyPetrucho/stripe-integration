import os
from decimal import Decimal

import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from cart.cart import Cart
from cart.forms import CartAddItemForm
from orders.models import Order
from payments.models import Item
from payments.service import exchange_to_rubles

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

        # Обрабатываем каждую позицию в заказе
        for order_item in order.items.all():
            item = order_item.item  # Доступ к объекту Item через OrderItem
            price_in_rubles = order_item.price

            if item.currency == "usd":
                # Конвертация USD в RUB
                price_in_rubles = order_item.price * exchange_to_rubles()

            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(price_in_rubles * Decimal("100")),
                        "currency": "rub",  # Все цены передаются в рублях
                        "product_data": {
                            "name": item.name,  # Название товара из модели Item
                        },
                    },
                    "quantity": order_item.quantity,
                }
            )

        # Создание сессии оплаты Stripe
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    else:
        return render(request, "payments/item/process.html", locals())


def item_list(request):
    items = Item.objects.all()
    cart = Cart(request)
    total_cost_in_rubles = cart.get_total_price_in_rubles()
    context = {"items": items, "total_cost_in_rubles": total_cost_in_rubles}
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
