from rest_framework.serializers import ModelSerializer

from orders.models import Order, OrderItem
from payments.models import Item


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ("name", "description", "price", "currency")


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", [])
        # Обновление полей заказа
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновление или создание связанных элементов заказа
        for item_data in items_data:
            item_id = item_data.get("id")
            if item_id:  # Существующий элемент заказа
                item = OrderItem.objects.get(id=item_id, order=instance)
                for attr, value in item_data.items():
                    setattr(item, attr, value)
                item.save()
            else:  # Новый элемент заказа
                OrderItem.objects.create(order=instance, **item_data)

        return instance
