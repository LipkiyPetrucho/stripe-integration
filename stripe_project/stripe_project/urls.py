from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cart/", include("cart.urls", namespace="cart")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("coupons/", include("coupons.urls", namespace="coupons")),
    path("", include("payments.urls", namespace="payments")),
]
