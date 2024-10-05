from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from cart.cart import Cart
from coupons.models import Tax
from orders.forms import OrderCreateForm
from orders.models import OrderItem


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if cart.coupon:
                    order.coupon = cart.coupon
                    order.discount = cart.coupon.discount
                order.save()

                tax_rates = Tax.objects.all()
                print(f"tax_rates: {tax_rates}")
                if tax_rates.exists():
                    order.tax.set(tax_rates)

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        item=item["product"],
                        price=item["price"],
                        quantity=item["quantity"],
                        currency=item["currency"],
                    )
                for order_item in order.items.all():
                    print(
                        f"OrderItem: ID={order_item.id},"
                        f" OrderID={order_item.order.id},"
                        f" Item={order_item.item.name},"
                        f" Price={order_item.price},"
                        f" Quantity={order_item.quantity}"
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
