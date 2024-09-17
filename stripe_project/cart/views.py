from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import Cart
from cart.forms import CartAddItemForm
from payments.models import Item


@require_POST
def cart_add(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    form = CartAddItemForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(item=item, quantity=cd["quantity"], override_quantity=cd["override"])
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddItemForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    total_cost_in_rubles = cart.get_total_price_in_rubles()

    return render(request, "cart/detail.html", {"cart": cart,
                                                "total_cost_in_rubles": total_cost_in_rubles})
