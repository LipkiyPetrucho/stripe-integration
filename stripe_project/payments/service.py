import os
from datetime import datetime
from decimal import Decimal

import pytz
import requests
import stripe
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Sum
from django.http import JsonResponse

domain = settings.DOMAIN
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")


def get_current_date() -> str:
    """Получение текущей даты, перевод в строку"""
    timezone = pytz.timezone("Europe/Moscow")
    get_now_with_tz = timezone.localize(datetime.now())
    current_date = get_now_with_tz.strftime("%d.%m.%Y")
    return current_date


def exchange_to_rubles() -> Decimal:
    """Перевод долларов в рубли по курсу"""
    current_date = get_current_date()
    url = "http://www.cbr.ru/scripts/XML_daily.asp?"
    params = {"date_req": current_date}
    request = requests.get(url, params)
    soup = BeautifulSoup(request.content, "lxml-xml")
    dollar_rate = soup.find(ID="R01235").Value.string
    dollar_rate = Decimal(dollar_rate.replace(",", ".")).quantize(Decimal("1.00"))
    return dollar_rate


def get_total_price(items) -> Decimal:
    """Функция, для получения общей суммы заказа"""
    total_price_rub, total_price_usd = 0, 0
    if items.filter(currency="rub"):
        total_price_rub = items.filter(currency="rub").aggregate(Sum("price"))[
            "price__sum"
        ]
        print(f"Сумма в RUB: {total_price_rub}")
    if items.filter(currency="usd"):
        total_price_usd = (
            items.filter(currency="usd").aggregate(Sum("price"))["price__sum"]
            * exchange_to_rubles()
        )
        print(f"Сумма в USD (в рублях): {total_price_usd}")
    total_price = Decimal(total_price_rub + total_price_usd).quantize(Decimal("1.00"))
    print(f"Итоговая сумма: {total_price}")
    return total_price


def create_stripe_checkout(item):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": item.currency,
                        "unit_amount": int(item.price * Decimal("100")),
                        "product_data": {
                            "name": item.name,
                            "description": item.description,
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{domain}/completed/",
            cancel_url=f"{domain}/canceled/",
        )
    except Exception as e:
        return JsonResponse({"error": str(e)})
    return JsonResponse({"sessionId": session.id})


def create_payment_intent(order):
    try:
        intent = stripe.PaymentIntent.create(
            unit_amount=int(order.get_total_price * Decimal("100")),
            currency=order.item.currency,
            automatic_payment_methods={
                "enabled": True,
            },
            metadata={"order_id": order.id},
        )
        return JsonResponse({"clientSecret": intent["client_secret"]})
    except Exception as e:
        return JsonResponse({"error": str(e)})
