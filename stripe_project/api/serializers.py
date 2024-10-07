from rest_framework.serializers import ModelSerializer

from orders.models import Order
from payments.models import Item


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ("name", "description", "price", "currency")


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "items")
