from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('tambah/', views.member_create, name='member_create'),
    path('impor-csv/', views.member_import_csv, name='member_import_csv'),
    path('impor-csv/template/', views.download_import_template, name='download_import_template'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('<int:pk>/ubah/', views.member_update, name='member_update'),
]
