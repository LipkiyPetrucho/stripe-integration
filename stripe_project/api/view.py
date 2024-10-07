from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers import ItemSerializer
from payments.models import Item
from payments.views import buy_order_intent


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


@api_view(["GET"])
def api_buy_item(request, pk):
    try:
        item = get_object_or_404(Item, pk=pk)
        return Response(item)
    except Http404:
        return Response(
            {"detail": "Товар с данным id не найден"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def api_create_payment_intent(request):
    try:
        response = buy_order_intent(request)
        return response
    except Http404:
        return Response(
            {"detail": "Заказ с данным id не найден"},
            status=status.HTTP_400_BAD_REQUEST,
        )
