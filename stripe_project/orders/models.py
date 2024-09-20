from decimal import Decimal

from django.db import models

from payments.models import Item
from payments.service import exchange_to_rubles


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"Order {self.id}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name="order_items", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(
        max_length=3,
        default="rub",
    )

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        total_price_rub = 0
        total_price_usd = 0
        if self.currency == "rub":
            total_price_rub += self.price * self.quantity
        elif self.currency == "usd":
            total_price_usd += self.price * self.quantity * exchange_to_rubles()
        return Decimal(total_price_rub + total_price_usd).quantize(Decimal("1.00"))
