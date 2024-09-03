from django.urls import path
from .views import buy_item, item_detail, payment_completed, payment_canceled

app_name = "payment"
urlpatterns = [
    path("buy/<int:id>/", buy_item, name="buy_item"),
    path("item/<int:id>/", item_detail, name="item_detail"),
    path("completed/", payment_completed, name="completed"),
    path("canceled/", payment_canceled, name="canceled"),
]
