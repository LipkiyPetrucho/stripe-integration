import os
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse

domain = settings.DOMAIN
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")

def create_stripe_checkout(item):
    """Создание сессии stripe"""
    try:
        session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": item.currency,
                                "unit_amount": int(item.price * Decimal("100")),
                                "product_data": {
                                    "name": item.name,
                                    "description": item.description,
                                },
                            },
                            "quantity": 1,
                        }
                    ],
                    mode="payment",
                    success_url=f"{domain}/completed/",
                    cancel_url=f"{domain}/canceled/",
                )
    except Exception as e:
        return JsonResponse({"error": str(e)})
    return JsonResponse({"sessionId": session.id})
