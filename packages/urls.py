from django.urls import path
from . import views

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('tambah/', views.package_create, name='package_create'),
    path('<int:pk>/ubah/', views.package_update, name='package_update'),
    path('<int:pk>/toggle/', views.package_toggle_active, name='package_toggle_active'),
]

