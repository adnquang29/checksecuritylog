# CheckSecurityLog

CheckSecurityLog là một project Python sử dụng Flask (hoặc Django) và MariaDB/MySQL để quản lý dữ liệu bảo mật/log.

---

## Chạy project

Để chạy project sau khi clone repository, làm theo các bước sau:

### 1. Truy cập vào thư mục dự án

```bash
cd checksecuritylog
```

### 2. Tạo và kích hoạt môi trường ảo

```bash
python3 -m venv venv

# Linux/MacOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Cài đặt các package cần thiết

```bash
pip install -r requirements.txt
```

### 4. Thiết lập biến môi trường (nếu dùng Flask)

```bash
# Linux/MacOS
export FLASK_APP=checksecuritylog.py   # Hoặc tên file chính của app
export FLASK_ENV=development            # Tùy chọn, bật debug mode

# Windows
set FLASK_APP=checksecuritylog.py
set FLASK_ENV=development
```

### 5. Khởi chạy ứng dụng

```bash
# Flask
flask run

# Django
python manage.py runserver
```

> Lưu ý: Kiểm tra README gốc hoặc file main của project để xác định tên file Flask app chính xác.

---

## Cấu hình MariaDB/MySQL

Trước khi chạy ứng dụng, đảm bảo file `config.py` hoặc biến môi trường trỏ đúng tới database:

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@localhost/dbname"
```

### Reset MariaDB/MySQL (nếu cần)

```bash
sudo systemctl stop mysql  # hoặc mariadb
sudo rm -rf /var/lib/mysql/*
sudo rm -rf /var/log/mysql/*
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### Tạo database và user cho project

```bash
sudo mysql -u root
```

Trong MySQL shell:

```sql
CREATE DATABASE checksecuritylog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'checkuser'@'localhost' IDENTIFIED BY 'matkhau';
GRANT ALL PRIVILEGES ON checksecuritylog.* TO 'checkuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

> Thay `matkhau` bằng mật khẩu bạn chọn.

---

## Quản lý database với Flask-Migrate

Nếu dùng Flask-Migrate để quản lý schema:

```bash
# Khởi tạo migration (chỉ lần đầu)
flask db init

# Tạo migration khi models thay đổi
flask db migrate -m "Mô tả thay đổi"

# Áp dụng migration lên database
flask db upgrade

# Đưa schema về trạng thái gốc (nếu cần)
flask db downgrade base
```

---

## Chuỗi hoàn chỉnh chạy project

1. Tạo environment và cài dependencies
2. Cấu hình biến môi trường Flask
3. Tạo database và user MariaDB/MySQL
4. Chạy Flask-Migrate (init → migrate → upgrade)
5. Chạy ứng dụng (`flask run` hoặc `python manage.py runserver`)
