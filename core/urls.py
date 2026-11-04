from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pengingat-wa/', views.wa_reminders, name='wa_reminders'),
    path('laporan/', views.reports_view, name='reports_view'),
    path('owner/backup-db/', views.backup_database, name='backup_database'),
]
