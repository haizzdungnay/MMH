# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time

# Import các hàm và model cần thiết
from learning_log.crypto_utils import hmac_sha256_c
from users.models import Profile


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.
        form = UserCreationForm()
    else:
        # Process completed form.
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # Log the user in and then redirect to home page.
            login(request, new_user)
            return redirect('learning_logs:index')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'registration/register.html', context)

# --- VIEW API MỚI ĐỂ TẠO TOKEN ---

@csrf_exempt # Bỏ qua kiểm tra CSRF cho API login
def api_login(request):
    """
    Handles user login via API and returns a token.
    Expects a POST request with a JSON body: {"username": "...", "password": "..."}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    # Xác thực người dùng bằng thông tin đăng nhập
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # LẤY SECRET KEY TỪ PROFILE CỦA USER TRONG DB
        try:
            user_secret_key = user.profile.secret_key.encode('utf-8')
        except Profile.DoesNotExist:
            # Lỗi này không nên xảy ra nếu signal hoạt động đúng
            return JsonResponse({'error': 'Critical: User profile or secret key not found'}, status=500)
        
        # TẠO TOKEN
        user_id_bytes = str(user.id).encode('utf-8')
        current_timestamp = int(time.time())
        
        # Gọi hàm hmac_sha256_c từ crypto_utils
        token = hmac_sha256_c(user_secret_key, user_id_bytes, current_timestamp)

        # Trả về thông tin cho client
        return JsonResponse({
            'message': 'Login successful!',
            'user_id': user.id,
            'token': token,
            'timestamp': current_timestamp
        })
    else:
        # Nếu xác thực thất bại
        return JsonResponse({'error': 'Invalid credentials'}, status=401)