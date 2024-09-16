from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CompletedPayView,
    CanceledPayView,
    ItemsListView,
    ItemDetailView,
)

app_name = "payment"
urlpatterns = [
    path("", ItemsListView.as_view(), name="item_list"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("buy/<int:pk>/", CreateCheckoutSessionView.as_view(), name="buy_item"),
    path("completed/", CompletedPayView.as_view(), name="completed"),
    path("canceled/", CanceledPayView.as_view(), name="canceled"),
]
