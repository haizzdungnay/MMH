# Ứng dụng Learning Log với Xác thực SHA‑256 C + Salt

Dự án này xây dựng trên **Project 3** của cuốn *Python Crash Course* (Eric Matthes) và hướng dẫn *Learning Log* của Django, **mở rộng** cơ chế bảo mật bằng cách sử dụng **thuật toán SHA‑256 viết bằng C** và **per-user salt**.

## Những chức năng đã triển khai

1. **Băm mật khẩu tùy chỉnh**: Sử dụng thư viện C triển khai SHA‑256 (`src/sha256.c`), tích hợp vào Python qua `ctypes` (`users/sha256_c.py`).
2. **Salt riêng cho mỗi user**: Mỗi tài khoản sinh một **salt** ngẫu nhiên 16 byte (gồm 32 ký tự hex) và lưu trong model `Profile`.
3. **Mở rộng User model**: Tạo model `Profile` liên kết OneToOne với `auth_user` để lưu `salt`, `password_hash` và `secret_key`.
4. **Flow Đăng ký (Register)**:

   * Override view `register` để sau khi tạo `User`, gọi `profile.set_password(raw_password)`
   * Tự động sinh salt và hash trước khi lưu vào database.
5. **Flow Đăng nhập (Login)**:

   * Dùng view custom hoặc backend, gọi `profile.check_password(input_password)` để xác thực.
6. **Chuyển sang SQLite**: Mặc định sử dụng SQLite (`db.sqlite3`) cho phát triển local, dễ dàng kiểm tra dữ liệu `users_profile`.
7. **Hướng dẫn build thư viện C**: Có hướng dẫn biên dịch `sha256.c` thành `sha256.dll` (Windows) hoặc `libsha256.so` (Linux).
8. **Cấu hình môi trường**: Bao gồm `requirements.txt` và `.gitignore` hỗ trợ cài đặt nhanh và quản lý file bỏ qua.

## Yêu cầu ban đầu (Prerequisites)

* **Python 3.10 hoặc 3.11** (Django 5.2 không tương thích với 3.13+).
* **C compiler**: GCC (Linux/macOS) hoặc MSVC (Windows).
* **Virtual environment**: `venv`.

## Hướng dẫn thiết lập (Setup)

1. **Clone repository**:

   ```bash
   git clone <repo_url>
   cd <project_root>
   ```
2. **Tạo & kích hoạt virtualenv**:

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. **Cài dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Biên dịch thư viện SHA‑256**:

   * **Linux**:

     ```bash
     gcc -shared -fPIC src/sha256.c -o users/libsha256.so
     ```
   * **Windows (MSVC)**:

     ```cmd
     cl /LD src\sha256.c /Fe:users\sha256.dll
     ```
5. **Chạy migrate** (SQLite tạo `db.sqlite3`):

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. **Tạo superuser (tuỳ chọn)**:

   ```bash
   python manage.py createsuperuser
   ```
7. **Chạy development server**:

   ```bash
   python manage.py runserver
   ```

   Truy cập: `http://127.0.0.1:8000/`

## Cách sử dụng (Usage)

* **Đăng ký**: Truy cập `/users/register/`, nhập username + password → salt và hash tự động sinh và lưu.
* **Đăng nhập**: Truy cập `/users/login/`, nhập credentials → gọi `profile.check_password()` để xác thực.
* **Kiểm tra dữ liệu**: Dùng DB Browser for SQLite mở `db.sqlite3`, chọn bảng `users_profile` xem các trường `salt`, `password_hash`, `user_id`.

## Cấu trúc thư mục chính

```
├── learning_log/            # Cấu hình project Django
├── learning_logs/           # Ứng dụng chính (Topic, Entry,...)
├── users/                   # Ứng dụng xác thực mở rộng
│   ├── sha256_c.py          # Wrapper ctypes cho thư viện C
│   ├── models.py            # Profile model với salt và hash logic
│   ├── views.py             # Views register & login
│   └── migrations/          # Migration tự động
├── src/                     # Thư viện C SHA-256 (src/sha256.c)
├── db.sqlite3               # SQLite database
├── requirements.txt         # Danh sách gói Python
├── .gitignore               # Quy tắc bỏ qua file
└── manage.py                # Django CLI utility
```

## Kế hoạch nâng cấp (Next Steps)

* **Key Stretching**: Kết hợp PBKDF2 hoặc Argon2 để tăng độ an toàn mật khẩu.
* **Hardware Acceleration**: Tận dụng SIMD/ARM Crypto module để tăng tốc độ SHA‑256.
* **HMAC & Token Auth**: Mở rộng `hmac_sha256` để ký token cho API.
* **CI/CD & Fuzz Testing**: Thiết lập pipeline tự động build, kiểm thử tĩnh và fuzz-tests cho code C.

---

*Hoàn thành như một dự án minh chứng ứng dụng SHA‑256 chuẩn với forward‑thinking security.*
