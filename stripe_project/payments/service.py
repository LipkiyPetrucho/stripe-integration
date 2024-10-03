import os
from datetime import datetime
from decimal import Decimal

import pytz
import requests
import stripe
from bs4 import BeautifulSoup

from payments.models import Item

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


def get_total_price_from_cart(cart_items) -> Decimal:
    """Функция для получения общей суммы заказа."""
    total_price_rub, total_price_usd = 0, 0
    exchange_rate = exchange_to_rubles()

    # Извлекаем идентификаторы товаров из словарей
    item_ids = [
        item_id for item_id in cart_items.keys()
    ]  # Используем ключи (id товаров) из cart_items
    items = Item.objects.filter(id__in=item_ids)  # Получаем объекты товаров по id

    # Создаем словарь для быстрого доступа к товарам по их id
    items_dict = {item.id: item for item in items}

    for item_id, item_data in cart_items.items():
        item_price = Decimal(item_data["price"])
        item_quantity = item_data["quantity"]
        product = items_dict[int(item_id)]  # Получаем товар по его id

        # Проверяем валюту товара
        if product.currency == "rub":
            total_price_rub += item_price * item_quantity
        elif product.currency == "usd":
            total_price_usd += item_price * item_quantity * exchange_rate

    total_price = Decimal(total_price_rub + total_price_usd).quantize(Decimal("1.00"))
    print(f"Total price cart: {total_price}")
    return total_price


def get_total_price_from_items(items) -> Decimal:
    total_price_rub, total_price_usd = 0, 0
    for item in items:
        if item.currency == "rub":
            total_price_rub += item.price
        elif item.currency == "usd":
            total_price_usd += item.price * exchange_to_rubles()

    total_price = Decimal(total_price_rub + total_price_usd).quantize(Decimal("1.00"))
    print(f"Total price items: {total_price}")
    return total_price
