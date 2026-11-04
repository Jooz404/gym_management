from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_code', 'full_name', 'phone_wa', 'join_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'join_date')
    search_fields = ('member_code', 'full_name', 'phone_wa')
