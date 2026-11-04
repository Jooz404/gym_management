from django.urls import path
from .views import CustomLoginView, user_logout

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
]

