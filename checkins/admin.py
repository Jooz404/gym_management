from django.contrib import admin
from .models import Checkin


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    list_display = ('member', 'checked_in_at', 'method', 'result', 'recorded_by')
    list_filter = ('result', 'method', 'checked_in_at')
    search_fields = ('member__full_name', 'member__member_code')
