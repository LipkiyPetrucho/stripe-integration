import logging
from datetime import datetime
from decimal import Decimal

import pytz
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_current_date() -> str:
    """Получение текущей даты"""
    timezone = pytz.timezone("Europe/Moscow")
    get_now_with_tz = timezone.localize(datetime.now())
    current_date = get_now_with_tz.strftime("%d.%m.%Y")
    return current_date


def fetch_exchange_rate() -> Decimal:
    """Запрос курса доллара к рублю с ЦБ РФ"""
    current_date = get_current_date()
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    params = {"date_req": current_date}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml-xml")
        usd_tag = soup.find("Valute", ID="R01235")
        if not usd_tag:
            raise ValueError("Курс доллара не найден на странице ЦБ РФ.")
        value = usd_tag.find("Value").text
        dollar_rate = Decimal(value.replace(",", ".")).quantize(Decimal("1.00"))
        logger.info(f"Курс доллара успешно получен: {dollar_rate} RUB")
        return dollar_rate
    except Exception as e:
        logger.error(f"Ошибка при получении курса валют: {e}")
        raise RuntimeError("Не удалось получить курс валют.")


def get_exchange_rate() -> Decimal:
    """
    Получение курса доллара к рублю с кэшированием.
    Кэширует курс на 24 часа.
    """
    cache_key = "usd_to_rub_rate"
    exchange_rate = cache.get(cache_key)
    if exchange_rate is None:
        exchange_rate = fetch_exchange_rate()
        cache.set(cache_key, exchange_rate, timeout=settings.CACHE_TTL)
    return exchange_rate
