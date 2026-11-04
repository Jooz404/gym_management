from django.urls import path
from . import views

urlpatterns = [
    path('member/<int:member_id>/renew/', views.membership_create, name='membership_create'),
    path('payment/<int:payment_id>/receipt/', views.payment_receipt, name='payment_receipt'),
]

