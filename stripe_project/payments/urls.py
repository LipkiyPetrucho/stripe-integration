import webhooks
from django.urls import path
from . import webhooks
from .views import (
    buy_item,
    item_detail,
    payment_completed,
    payment_canceled,
    item_list,
    buy_order,
    buy_order_intent,
)

app_name = "payment"
urlpatterns = [
    path("", item_list, name="item_list"),
    path("item/<int:id>/", item_detail, name="item_detail"),
    path("buy/<int:id>/", buy_item, name="buy_item"),
    path("buy_order/", buy_order, name="buy_order"),
    path("buy_order_intent/", buy_order_intent, name="buy_order_intent"),
    path("completed/", payment_completed, name="completed"),
    path("canceled/", payment_canceled, name="canceled"),
    path("payment/webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
]
