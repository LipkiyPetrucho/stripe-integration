from decimal import Decimal

from django.conf import settings

from payments.models import Item
from coupons.models import Coupon
from payments.utils.currency import get_exchange_rate


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # сохранить текущий примененный купон
        self.coupon_id = self.session.get("coupon_id")

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
        products = Item.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]["product"] = product  # Добавляем обратно в 'cart'
            cart[str(product.id)]["currency"] = product.currency
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        total_price_rub = Decimal("0.00")
        total_price_usd = Decimal("0.00")
        exchange_rate = get_exchange_rate()
        for item in self.cart.values():
            if item["currency"] == "rub":
                total_price_rub += item["price"] * item["quantity"]
            elif item["currency"] == "usd":
                total_price_usd += item["price"] * item["quantity"] * exchange_rate
        return Decimal(total_price_rub + total_price_usd).quantize(Decimal("1.00"))

    def clear(self):
        self.session["coupon_id"] = None
        del self.session[settings.CART_SESSION_ID]
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
