from decimal import Decimal

from django.conf import settings

from payments.models import Item
from payments.service import get_total_price_from_cart, exchange_to_rubles


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Добавление товара в корзину или обновление его количества.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Прокрутить товарные позиции корзины в цикле и
        получить товары из базы данных.
        """
        product_ids = self.cart.keys()
        print(f"__iter__: Идентификаторы товаров из корзины: {product_ids}")
        products = Item.objects.filter(id__in=product_ids)
        print(f"Полученные объекты Item: {products}")
        cart = self.cart.copy()
        print(f"Первоначальное состояние корзины: {cart}")
        for product in products:
            cart[str(product.id)]["product"] = product  # Добавляем обратно в 'cart'
            cart[str(product.id)]["currency"] = product.currency
            print(f"информация о добавленном товаре: {product.name}, ID: {product.id}")
        print(f"состояние корзины после добавления товаров: {cart}")
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            print(f"состояние каждого элемента корзины: {item}")
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        total_price_rub = 0
        total_price_usd = 0
        for item in self.cart.values():
            if item["currency"] == "rub":
                total_price_rub += item["price"] * item["quantity"]
            elif item["currency"] == "usd":
                total_price_usd += item["price"] * item["quantity"] * exchange_to_rubles()
        return Decimal(total_price_rub + total_price_usd).quantize(Decimal("1.00"))

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_price_in_rubles(self):
        """Возвращает общую стоимость товаров в корзине, конвертируя их в рубли."""
        return get_total_price_from_cart(self.cart)  # Передаем всю корзину
