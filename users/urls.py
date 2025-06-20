"""Defines URL patterns for users"""

from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'
urlpatterns = [
    # Include default auth urls.
    path('', include('django.contrib.auth.urls')),
    # Registration page.
    path('register/', views.register, name='register'),
    # Login page with custom template.
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
]
