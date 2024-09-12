from decimal import Decimal

from django.test import TestCase

from payments.service import get_current_date, exchange_to_rubles


class DateUtilsTestCase(TestCase):
    def test_get_current_date(self):
        result = get_current_date() # Получение текущей даты
        print(f"Результат работы функции get_current_date: {result}")
        self.assertIsInstance(result, str)  # Проверка, что результат - строка
        self.assertRegex(result, r'^\d{2}\.\d{2}\.\d{4}$')  # Проверка формата "дд.мм.гггг"


class CurrencyExchangeTestCase(TestCase):
    def test_exchange_to_rubles(self):
        result = exchange_to_rubles()
        print(f"Результат работы функции exchange_to_rubles: {result}")
        self.assertIsInstance(result, Decimal)
        self.assertGreater(result, Decimal(0))