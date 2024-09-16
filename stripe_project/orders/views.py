from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView

from orders.forms import OrderCreateForm
from orders.models import OrderItem, Order
from payments.models import Item
from payments.service import create_payment_intent


domain_url = settings.DOMAIN


class CreateOrderView(View):
    def post(self, request):
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Сохраняем новый заказ
            order = form.save()

            # Получаем выбранные товары и количество
            item_ids = request.POST.getlist('item_ids')
            for item_id in item_ids:
                item = get_object_or_404(Item, pk=item_id)
                OrderItem.objects.create(order=order, item=item, price=item.price, quantity=1)  # Добавляем товары в заказ

            return redirect("orders:orders_list")
        else:
            form = OrderCreateForm()
        return render(request, 'orders/order/add_to_order.html', {'form': form})


class OrderPaymentView(TemplateView):
    template_name = "orders/order/order_detail.html"

    def get_context_data(self, **kwargs):
        order_id = self.kwargs["pk"]
        order = get_object_or_404(Order, id=order_id)
        order_items = order.items.all()  # Получаем все OrderItem, связанные с заказом
        stripe_pub_key = settings.STRIPE_PUBLISHABLE_KEY
        context = super().get_context_data(**kwargs)
        context.update({
            "items": order_items,  # Передаём OrderItem объекты в контекст
            "order": order,
            "clientSecret": stripe_pub_key,
            "stripe_pub_key": stripe_pub_key,
            "domain_url": domain_url,
        })
        return context


class OrderListView(ListView):
    model = Order
    template_name = 'orders/order/orders_list.html'
    context_object_name = "orders"
