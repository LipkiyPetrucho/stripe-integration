from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    create_checkout_session, CompletedPayView, CanceledPayView, ItemsListView, ItemDetailView,
)

app_name = "payment"
urlpatterns = [
    path("", ItemsListView.as_view(), name="item_list"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("buy/<int:pk>/", CreateCheckoutSessionView.as_view(), name="buy_item"),
    # path("buy_order/", buy_order, name="buy_order"),
    path(
        "create-checkout-session/<str:session_id>/",
        create_checkout_session,
        name="create_checkout_session",
    ),
    path("completed/", CompletedPayView.as_view(), name="completed"),
    path("canceled/", CanceledPayView.as_view(), name="canceled"),
]
