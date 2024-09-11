from django.contrib import admin

from payments.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "price",
        "currency",
    ]
    search_fields = ["name", "description"]
    ordering = ["name"]