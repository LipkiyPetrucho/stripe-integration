from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.api.view import ItemViewSet

router = DefaultRouter()
router.register(r"item", ItemViewSet, basename="items")

urlpatterns = [
    path("", include(router.urls)),
]
