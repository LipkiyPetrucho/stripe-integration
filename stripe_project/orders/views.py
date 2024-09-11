from django.shortcuts import render, redirect
from django.urls import reverse

from orders.forms import OrderCreateForm
from orders.models import OrderItem


def order_create(request):
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            request.session["order_id"] = order.id
            return redirect(reverse("payment:buy_order"))
    else:
        form = OrderCreateForm()
    return render(request, "orders/order/create.html", {"form": form})
