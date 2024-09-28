from django.contrib import admin

from coupons.models import Coupon, Tax


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "valid_from", "valid_to", "discount", "active"]
    list_filter = ["active", "valid_from", "valid_to"]
    search_fields = ["code"]


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ["name", "rate"]
