
# Project: Learning Log – Web ứng dụng Django

Ứng dụng này cho phép người dùng ghi lại những chủ đề mà họ đang học, cũng như những mục học tập chi tiết cho từng chủ đề đó.

---
Link Web: https://ptit-django-2025-e99c2da87268.herokuapp.com/

Tài khoản Admin:

Username: admin

Password: Matkhau@123

---

## Cách chạy dự án (localhost)

### 1. Clone project

```bash
git clone https://github.com/T-Hieu312/Python_Web_Applications.git
cd Python_Web_Applications
```

### 2. Tạo virtual environment (không dùng `ll_env` của người khác)

```bash
# Windows:
python -m venv env
env\Scripts\activate

# macOS/Linux:
python3 -m venv env
source env/bin/activate
```

### 3. Cài các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 4. Chạy migrations & tạo database

```bash
python manage.py migrate
```

### 5. (Tuỳ chọn) Tạo tài khoản quản trị

```bash
python manage.py createsuperuser
```

### 6. Chạy server

```bash
python manage.py runserver
```

Vào trình duyệt và mở địa chỉ:
```
http://127.0.0.1:8000/
```

---

## Ghi chú

- Không cần dùng thư mục `ll_env/` có sẵn. Tự tạo môi trường ảo là tốt nhất.
- Nếu lỗi: `ModuleNotFoundError`, hãy chắc rằng bạn đã chạy `pip install -r requirements.txt`.
