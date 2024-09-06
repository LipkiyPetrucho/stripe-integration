from django.urls import path

from cart.views import cart_detail, cart_add, cart_remove

app_name = "cart"

urlpatterns = [
    path("", cart_detail, name="cart_detail"),
    path("add/<int:item_id>/", cart_add, name="cart_add"),
    path("remove/<int:item_id>/", cart_remove, name="cart_remove"),
]
