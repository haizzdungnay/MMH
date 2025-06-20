# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
def register(request):
    """Đăng ký người dùng mới với SHA-256 + salt."""

    if request.method != 'POST':
        # Hiển thị form đăng ký trống
        form = UserCreationForm()
    else:
        # Xử lý khi submit form
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save(commit=False)  # tạm hoãn lưu DB
            new_user.save()  # lưu trước để tạo instance Profile qua signal

            # Gọi set_password để sinh salt + băm bằng SHA256 C
            raw_password = form.cleaned_data['password1']
            new_user.profile.set_password(raw_password)

            # Đăng nhập và chuyển hướng
            login(request, new_user)
            return redirect('learning_logs:index')

    # Hiển thị form (ban đầu hoặc không hợp lệ)
    context = {'form': form}
    return render(request, 'registration/register.html', context)
