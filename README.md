https://github.com/BugBusterBot/microblog

# Chạy project

Để chạy project checksecuritylog sau khi bạn đã git clone repository về, bạn cần thực hiện một số bước sau tuỳ thuộc vào công nghệ mà repository sử dụng. Dưới đây là các bước tổng quát áp dụng cho dự án Python (vì microblog thường dùng Flask hoặc Django):

1. Truy cập vào thư mục dự án:
bash
cd microblog
2. Tạo và kích hoạt môi trường ảo (nên dùng):
bash
python3 -m venv venv
source venv/bin/activate        # Đối với Linux/MacOS
venv\Scripts\activate           # Đối với Windows
3. Cài đặt các package cần thiết:
Thường sẽ có file requirements.txt, bạn hãy chạy:

bash
pip install -r requirements.txt
4. Thiết lập biến môi trường (nếu cần)
Nếu là Flask, bạn cần export FLASK_APP:

bash
export FLASK_APP=microblog.py   # hoặc tên file main của ứng dụng
export FLASK_ENV=development    # (optional) bật debug mode
Windows thì dùng:

cmd
set FLASK_APP=microblog.py
set FLASK_ENV=development
5. Khởi chạy ứng dụng
Nếu là Flask:

bash
flask run
Nếu là Django:

bash
python manage.py runserver
Lưu ý:

Có thể dự án đã có README.md hướng dẫn chi tiết. Bạn hãy kiểm tra file này để xem hướng dẫn cụ thể trong repository bạn vừa clone.
Tên file main của Flask app có thể khác (app.py, main.py hoặc microblog.py).

Lưu ý khi thao tác trên MySQL/MariaDB
Trước khi chạy các lệnh trên, đảm bảo file config của dự án (config.py hoặc biến môi trường) đã trỏ tới đúng connection string của MySQL hoặc MariaDB (ví dụ: mysql+pymysql://user:password@host/dbname).
Đảm bảo đã cài đặt các dependencies tương ứng như pymysql hoặc mysqlclient.
Ví dụ chu trình hoàn chỉnh
bash
# Khởi tạo migration (chỉ 1 lần đầu)
flask db init

# Tạo migration mới khi model thay đổi
flask db migrate -m "add tablename or modify..."

# Chạy migration (đẩy schema/tables lên DB)
flask db upgrade
Nếu DB lỗi, có thể dùng:

bash
flask db downgrade base   # hoặc sử dụng flask db downgrade <revision>
Rồi migrate/upgrade lại.

Bạn đã thực hiện đúng các bước để reset hoàn toàn MariaDB/MySQL về trạng thái mới tinh. Tổng kết lại, bạn đã:

Dừng dịch vụ MySQL (hoặc MariaDB):

bash
sudo systemctl stop mysql # hoặc mariadb
Xoá toàn bộ dữ liệu cũ:

bash
sudo rm -rf /var/lib/mysql/*
sudo rm -rf /var/log/mysql/*
Cài đặt lại database system tables:

bash
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
Khởi động lại MariaDB và enable dịch vụ:

bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
Tiếp theo: Làm việc với Flask-Migrate
Vì bây giờ MariaDB/MYSQL của bạn là mới, bạn cần:

Truy cập MariaDB để tạo 1 database mới mà ứng dụng Flask sẽ dùng (ví dụ tên là microblog):

bash
sudo mysql -u root
Trong MySQL shell:

SQL
CREATE DATABASE microblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'microbloguser'@'localhost' IDENTIFIED BY 'matkhau';
GRANT ALL PRIVILEGES ON microblog.* TO 'microbloguser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
(Thay matkhau bằng mật khẩu bạn chọn!)

Cấu hình lại chuỗi kết nối DB trong app Flask: Trong config.py hoặc .env:

Python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://microbloguser:matkhau@localhost/microblog"
Chạy lại các lệnh Flask-Migrate:
Bây giờ bạn có thể chạy lần lượt:

bash
flask db init         # Nếu chưa có folder migrations (một lần đầu)
flask db downgrade base  # (không bắt buộc, nếu bạn thực sự muốn đưa schema DB về trạng thái gốc base)
flask db migrate      # Tạo migration dựa vào models hiện tại
flask db upgrade      # Tạo bảng trong MariaDB
