from django.urls import path
from rest_framework.routers import SimpleRouter

from api.view import ItemViewSet, api_create_payment_intent

router = SimpleRouter()
router.register(r"item", ItemViewSet, basename="create_payment_intent")

urlpatterns = [
    path(
        "create_payment_intent/<int:pk>/",
        api_create_payment_intent,
        name="create_payment_intent",
    ),
]

urlpatterns += router.urls
