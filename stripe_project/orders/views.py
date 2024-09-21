from django.shortcuts import render, redirect
from django.urls import reverse

from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem
from payments.models import Item
from payments.service import get_total_price_from_items


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    item=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                    currency=item["currency"],
                )
            cart.clear()
            request.session["order_id"] = order.id
            return redirect(reverse("payment:buy_order"))
    else:
        form = OrderCreateForm()

    return render(
        request,
        "orders/order/create.html",
        {
            "cart": cart,
            "form": form,
        },
    )
