# users/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'users'
urlpatterns = [
    # Login page
    # SỬA Ở ĐÂY: Thay 'users/login.html' thành 'registration/login.html'
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Logout page
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration page
    path('register/', views.register, name='register'),

    # URL cho API login
    path('api/login/', views.api_login, name='api_login'),
]