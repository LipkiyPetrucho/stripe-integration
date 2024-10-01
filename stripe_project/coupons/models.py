import stripe
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage value (0 to 100)",
    )
    active = models.BooleanField()

    def __str__(self):
        return self.code


class Tax(models.Model):
    stripe_tax_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    name = models.CharField(verbose_name="НДС", max_length=100)
    rate = models.DecimalField(
        "Ставка налога (%)",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    def __str__(self):
        return f"id:{self.id} {self.name} ({self.rate}%)"

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"

    def create_stripe_tax_rate(self, jurisdiction="RU"):
        """
        Создаёт налоговую ставку в Stripe и сохраняет её ID.
        """
        if not self.stripe_tax_id:
            tax_rate = stripe.TaxRate.create(
                display_name=self.name,
                description=f"{self.rate}% {self.name}",
                jurisdiction=jurisdiction,
                percentage=float(self.rate),
                inclusive=False,
            )
            self.stripe_tax_id = tax_rate.id
            self.save()
        return self.stripe_tax_id
    # TODO: Check
