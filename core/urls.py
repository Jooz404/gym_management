from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('test/checkin/', views.feature_checkin_test, name='feature_checkin_test'),
    path('test/reports/', views.feature_reports_test, name='feature_reports_test'),
    path('test/wa/', views.feature_wa_test, name='feature_wa_test'),
]

