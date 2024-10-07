
from rest_framework.viewsets import ModelViewSet

from payments.api.serializers import ItemSerializer
from payments.models import Item


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer