from django.contrib import admin
from .models import Membership, Payment


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'package', 'start_date', 'end_date', 'status_label', 'created_at')
    list_filter = ('package', 'start_date', 'end_date')
    search_fields = ('member__full_name', 'member__member_code', 'package__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('membership', 'formatted_amount', 'method', 'status', 'paid_at', 'verified_by')
    list_filter = ('method', 'status', 'paid_at')
    search_fields = ('membership__member__full_name', 'membership__member__member_code')
