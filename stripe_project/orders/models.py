from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from coupons.models import Coupon, Tax
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
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(
        Coupon, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL
    )
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    tax = models.ManyToManyField(Tax, verbose_name="Налог", blank=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"Order {self.id}"

    def get_total_tax(self):
        total_tax = Decimal(0)
        for tax in self.tax.all():
            total_tax += self.get_total_cost_before_discount() * (
                tax.rate / Decimal(100)
            )
        return total_tax

    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        total_cost -= self.get_discount()
        return total_cost

    def get_stripe_url(self):
        if not self.stripe_id:
            # никаких ассоциированных платежей
            return ""
        if "_test_" in settings.STRIPE_SECRET_KEY:
            # путь Stripe для тестовых платежей
            path = "/test/"
        else:
            # путь Stripe для настоящих платежей
            path = "/"
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"

    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)


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
