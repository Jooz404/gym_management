from django.contrib import admin
from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'formatted_price', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
