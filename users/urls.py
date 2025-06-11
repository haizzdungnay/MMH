# users/urls.py

from django.urls import path
# Sửa đổi ở đây: Import LoginView và LogoutView trực tiếp từ django.contrib.auth
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'users'
urlpatterns = [
    # Login page - Sử dụng LoginView có sẵn của Django
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),

    # Logout page - Sửa đổi ở đây: Sử dụng LogoutView có sẵn của Django
    # Nó sẽ tự động xử lý việc đăng xuất và mặc định sẽ chuyển hướng đến trang chủ.
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration page
    path('register/', views.register, name='register'), # Sửa lỗi cú pháp: name='register'

    # URL cho API login, không thay đổi
    path('api/login/', views.api_login, name='api_login'),
]