# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets

# Import hàm băm từ module wrapper của bạn
from .sha256_c import sha256_c

class Profile(models.Model):
    """
    Mở rộng User với:
     - salt: 16 byte (hex 32 ký tự)
     - password_hash: hex SHA-256 (64 ký tự)
     - secret_key: dùng cho mục đích khác nếu cần
    """
    user          = models.OneToOneField(User, on_delete=models.CASCADE)
    salt          = models.CharField(max_length=32, blank=True)
    password_hash = models.CharField(max_length=64, blank=True)
    secret_key    = models.CharField(max_length=64, blank=True, unique=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def set_password(self, raw_password: str):
        """
        Gọi khi đăng ký hoặc đổi mật khẩu:
         1. Sinh salt
         2. Băm password+salt
         3. Lưu lại
        """
        # 1) Sinh 16-byte salt, encode hex thành 32 ký tự
        self.salt = secrets.token_hex(16)
        # 2) Tính SHA-256(password + salt) qua C lib
        self.password_hash = sha256_c((raw_password + self.salt).encode('utf-8'))
        # 3) Lưu Profile
        self.save()

    def check_password(self, raw_password: str) -> bool:
        """
        Gọi khi đăng nhập:
         - Băm input + salt
         - So sánh với password_hash lưu trong DB
        """
        computed = sha256_c((raw_password + self.salt).encode('utf-8'))
        return computed == self.password_hash

# Signal để tự tạo Profile khi User mới được tạo
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        # Sinh secret_key nếu bạn vẫn cần
        profile.secret_key = secrets.token_hex(32)
        profile.save()
