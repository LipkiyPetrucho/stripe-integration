import os
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from orders.models import Order
from payments.models import Item
from payments.service import create_stripe_checkout

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")


class CreateCheckoutSessionView(View):
    def get(self, request, **kwargs):
        item = get_object_or_404(Item, pk=kwargs["pk"])
        response = create_stripe_checkout(item)
        return response


# def buy_order(request):
#     order_id = request.session.get("order_id", None)
#     order = get_object_or_404(Order, id=order_id)
#     if request.method == "POST":
#         success_url = request.build_absolute_uri(reverse("payment:completed"))
#         cancel_url = request.build_absolute_uri(reverse("payment:canceled"))
#
#         items_by_currency = {}
#         for item in order.items.all():
#             if item.item.currency not in items_by_currency:
#                 items_by_currency[item.item.currency] = []
#             items_by_currency[item.item.currency].append(item)
#
#         session_ids = {} # Список для хранения идентификаторов сессий на разные валюты.
#         for currency, items in items_by_currency.items():
#             line_items = []
#             total_amount = 0
#
#             for item in items:
#                 line_items.append(
#                     {
#                         "price_data": {
#                             "unit_amount": int(item.price * Decimal("100")),
#                             "currency": currency,
#                             "product_data": {
#                                 "name": item.item.name,
#                             },
#                         },
#                         "quantity": item.quantity,
#                     }
#                 )
#                 total_amount += item.price * item.quantity
#
#             session_data = {
#                 "mode": "payment",
#                 "client_reference_id": order.id,
#                 "success_url": success_url,
#                 "cancel_url": cancel_url,
#                 "line_items": line_items,
#             }
#             session = stripe.checkout.Session.create(**session_data)
#             session_ids[currency] = [session.id, total_amount]
#
#             Payment.objects.create(
#                 order=order,
#                 currency=currency,
#                 amount=total_amount,
#                 session_id=session.id
#             )
#         return render(request, "payments/item/multiple_sessions.html", {"session_ids": session_ids})
#     else:
#         return render(request, "payments/item/process.html", locals())


class ItemsListView(ListView):
    model = Item
    template_name = "payments/item/item_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        return Item.objects.all().order_by("name")


class ItemDetailView(DetailView):
    model = Item
    template_name = "payments/item/item_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_publishable_key"] = stripe_publishable_key
        return context

    def get_object(self):
        return get_object_or_404(Item, pk=self.kwargs["pk"])


class CompletedPayView(TemplateView):
    template_name = "payments/completed.html"


class CanceledPayView(TemplateView):
    template_name = "payments/canceled.html"


def create_checkout_session(request, session_id):
    if request.method == "POST":
        try:
            # Проверяем существование сессии Stripe по session_id
            session = stripe.checkout.Session.retrieve(session_id)
            return JsonResponse(
                {"url": session.url}
            )  # Возвращаем URL для перенаправления
        except stripe.error.InvalidRequestError:
            return JsonResponse({"error": "Invalid session ID."}, status=400)
        except Exception as e:
            # Дополнительная обработка ошибок
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)
