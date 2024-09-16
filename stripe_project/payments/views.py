import os
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem
from payments.models import Item
from payments.service import create_stripe_checkout, create_payment_intent

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")


class CreateCheckoutSessionView(View):
    def get(self, request, **kwargs):
        item = get_object_or_404(Item, pk=kwargs["pk"])
        response = create_stripe_checkout(item)
        return response


class ItemsListView(ListView):
    model = Item
    template_name = "payments/item/item_list.html"
    context_object_name = "items"

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
