from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import Cart
from cart.forms import CartAddItemForm
from payments.models import Item
from payments.service import get_total_price_from_cart
from coupons.forms import CouponApplyForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    print(f"CARD_ADD -> cart: {vars(cart)}")
    product = get_object_or_404(Item, id=product_id)
    form = CartAddItemForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product, quantity=cd["quantity"], override_quantity=cd["override"]
        )
    print(f"ADD -> cart: {vars(cart)}")
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Item, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    total_cost_in_rubles = get_total_price_from_cart(
        cart.cart
    )  # Передаем значения корзины

    for item in cart:
        item["update_quantity_form"] = CartAddItemForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    coupon_apply_form = CouponApplyForm()
    return render(
        request,
        "cart/detail.html",
        {
            "cart": cart,
            "total_cost_in_rubles": total_cost_in_rubles,
            "coupon_apply_form": coupon_apply_form,
        },
    )
