from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkin_page, name='checkin_page'),
]

