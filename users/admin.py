from django.contrib import admin

# Register your models here.
# users/admin.py

from django.contrib import admin
from .models import Profile # Import model Profile bạn vừa tạo

# Đăng ký model Profile với trang admin
admin.site.register(Profile)