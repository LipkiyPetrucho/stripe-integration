from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from payments.models import Item
from payments.service import (
    get_current_date,
    exchange_to_rubles,
    get_total_price,
)


class DateUtilsTestCase(TestCase):
    """Получение текущего дня"""

    def test_get_current_date(self):
        result = get_current_date()  # Получение текущей даты
        print(f"Результат работы функции get_current_date: {result}")
        self.assertIsInstance(result, str)  # Проверка, что результат - строка
        self.assertRegex(
            result, r"^\d{2}\.\d{2}\.\d{4}$"
        )  # Проверка формата "дд.мм.гггг"


class CurrencyExchangeTestCase(TestCase):
    """ "Получить обменный курс"""

    def test_exchange_to_rubles(self):
        result = exchange_to_rubles()
        print(f"Результат работы функции exchange_to_rubles: {result}")
        self.assertIsInstance(result, Decimal)
        self.assertGreater(result, Decimal(0))


class GetTotalPriceTestCase(TestCase):
    """ "Получить общую сумму заказа"""

    def setUp(self):
        # Создание тестовых данных
        Item.objects.create(
            name="Item 1", description="Description 1", price=100.00, currency="rub"
        )
        Item.objects.create(
            name="Item 2", description="Description 2", price=2.00, currency="usd"
        )

    @patch("payments.service.exchange_to_rubles")
    def test_get_total_price(self, mock_exchange):
        mock_exchange.return_value = Decimal("75.00")  # Получение обменного курса
        items = Item.objects.all()  # Получение всех объектов
        total = get_total_price(items)
        print(f"Тестовая итоговая сумма: {total}")
        # Проверка, что итоговая сумма соответствует ожидаемому значению
        expected_total = Decimal("250.00")
        self.assertEqual(total, expected_total)


class CreateStripeCheckoutTestCase(TestCase):
    """ "Создание сеанса платежной карты"""

    def setUp(self):
        self.client = Client()
        self.item = Item.objects.create(
            name="Test Item",
            description="Test Description",
            price=100.00,
            currency="rub",
        )

    @patch("stripe.checkout.Session.create")
    def test_create_stripe_checkout_success(self, mock_create):
        """Успешное создание сеанса Stripe Checkout."""
        # Настраиваем мок, чтобы он возвращал желаемое значение
        mock_create.return_value = type("obj", (object,), {"id": "test_session_id"})
        response = self.client.get(
            reverse("payments:buy_item", kwargs={"pk": self.item.pk})
        )
        # Проверка, что ответ - это JSON с sessionId
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(), {"sessionId": "test_session_id"}
        )
        mock_create.assert_called_once()  # Проверяем, что метод был вызван один раз

    @patch("stripe.checkout.Session.create")
    def test_create_stripe_checkout_failure(self, mock_create):
        """Обработка ошибки при создании сеанса Stripe Checkout."""
        mock_create.side_effect = Exception("Stripe error")
        response = self.client.get(
            reverse("payments:buy_item", kwargs={"pk": self.item.pk})
        )
        # Проверка, что ответ содержит сообщение об ошибке
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {"error": "Stripe error"})
