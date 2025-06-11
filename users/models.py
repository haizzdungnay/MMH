from django.db import models

# Create your models here.
# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets # Thư viện chuẩn của Python để tạo chuỗi ngẫu nhiên an toàn

class Profile(models.Model):
    """Model để lưu thông tin mở rộng cho User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=64, blank=True, unique=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# Đây là một "Signal", nó sẽ được kích hoạt mỗi khi một đối tượng User được LƯU
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Tự động tạo Profile và secret_key khi một User mới được đăng ký.
    """
    if created: # Chỉ chạy khi User được TẠO MỚI
        profile = Profile.objects.create(user=instance)
        # Tạo một secret key ngẫu nhiên, an toàn với 32 bytes (64 ký tự hex)
        profile.secret_key = secrets.token_hex(32)
        profile.save()