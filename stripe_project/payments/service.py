import os
from datetime import datetime
from decimal import Decimal

import pytz
import requests
import stripe
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Sum

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
    print(f"Курс доллара в рублях: {dollar_rate}")
    return dollar_rate


def get_total_price_service(items) -> Decimal:
    """Функция, для получения общей суммы заказа"""
    total_price_rub, total_price_usd = 0, 0
    for item in items:
        print(f"Товар: {item.name}, валюта: {item.currency}, цена: {item.price}")
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