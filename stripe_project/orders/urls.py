from django.urls import path

from orders.views import CreateOrderView, OrderListView, OrderPaymentView

app_name = "orders"
urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders_list"),
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path("order/<int:pk>/", OrderPaymentView.as_view(), name="view_order"),
]
