from django.db import models
from django.urls import reverse


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("payments:item_detail", args=[self.id])
