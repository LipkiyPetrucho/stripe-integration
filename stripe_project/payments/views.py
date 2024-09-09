import os
from decimal import Decimal

import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from cart.forms import CartAddItemForm
from orders.models import Order, Payment
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

        items_by_currency = {}
        for item in order.items.all():
            if item.item.currency not in items_by_currency:
                items_by_currency[item.item.currency] = []
            items_by_currency[item.item.currency].append(item)

        session_ids = {} # Список для хранения идентификаторов сессий на разные валюты.
        for currency, items in items_by_currency.items():
            line_items = []
            total_amount = 0

            for item in items:
                line_items.append(
                    {
                        "price_data": {
                            "unit_amount": int(item.price * Decimal("100")),
                            "currency": currency,
                            "product_data": {
                                "name": item.item.name,
                            },
                        },
                        "quantity": item.quantity,
                    }
                )
                total_amount += item.price * item.quantity

            session_data = {
                "mode": "payment",
                "client_reference_id": order.id,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "line_items": line_items,
            }
            session = stripe.checkout.Session.create(**session_data)
            session_ids[currency] = session.id

            Payment.objects.create(
                order=order,
                currency=currency,
                amount=total_amount,
                session_id=session.id
            )

        return render(request, "payments/item/multiple_sessions.html", {"session_ids": session_ids})
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


def create_checkout_session(request, session_id):
    if request.method == 'POST':
        try:
            # Проверяем существование сессии Stripe по session_id
            session = stripe.checkout.Session.retrieve(session_id)
            return JsonResponse({'url': session.url})  # Возвращаем URL для перенаправления
        except stripe.error.InvalidRequestError:
            return JsonResponse({'error': 'Invalid session ID.'}, status=400)
        except Exception as e:
            # Дополнительная обработка ошибок
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)