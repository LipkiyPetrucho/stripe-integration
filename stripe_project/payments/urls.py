from django.urls import path
from .views import (
    buy_item,
    item_detail,
    payment_completed,
    payment_canceled,
    item_list,
    buy_order, create_checkout_session,
)

app_name = "payment"
urlpatterns = [
    path("", item_list, name="item_list"),
    path("item/<int:id>/", item_detail, name="item_detail"),
    path("buy/<int:id>/", buy_item, name="buy_item"),
    path("buy_order/", buy_order, name="buy_order"),
    path('create-checkout-session/<str:session_id>/', create_checkout_session, name='create_checkout_session'),
    path("completed/", payment_completed, name="completed"),
    path("canceled/", payment_canceled, name="canceled"),
]
