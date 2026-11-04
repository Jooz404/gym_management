from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('packages/', include('packages.urls')),
    path('memberships/', include('memberships.urls')),
    path('checkin/', include('checkins.urls')),
    path('', include('core.urls')),
]
