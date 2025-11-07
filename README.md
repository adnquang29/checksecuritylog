https://github.com/BugBusterBot/microblog

# Chạy project

Để chạy project checksecuritylog sau khi bạn đã git clone repository về, bạn cần thực hiện một số bước sau tuỳ thuộc vào công nghệ mà repository sử dụng. Dưới đây là các bước tổng quát áp dụng cho dự án Python (vì microblog thường dùng Flask hoặc Django):

1. Truy cập vào thư mục dự án:
bash
cd microblog
2. Tạo và kích hoạt môi trường ảo (nên dùng):
bash
python -m venv venv
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

Để reset một database MariaDB (hoặc MySQL) về "mới hoàn toàn", để đảm bảo bạn có môi trường sạch khi chạy các lệnh Flask-Migrate/Alembic như:

flask db init
flask db downgrade base
flask db migrate
flask db upgrade
Hãy làm theo các bước sau:

1. Xóa database cũ và tạo lại database mới
Giả sử tên database của bạn là microblog.

Đăng nhập MySQL/MariaDB:

bash
mysql -u <username> -p
# Nhập password
Sau đó thực hiện các lệnh SQL sau:

SQL
DROP DATABASE IF EXISTS microblog;
CREATE DATABASE microblog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
2. (Tùy chọn) Xoá thư mục migrations trong project Flask
Nếu bạn muốn reset migration script về ban đầu (nên làm nếu có quá nhiều thay đổi, tránh lỗi):

bash
rm -rf migrations
3. Chạy lại các lệnh migrate
bash
# (Chỉ chạy 1 lần đầu tiên)
flask db init

# Tạo migration
flask db migrate -m "initial migration"

# Đẩy cấu trúc lên database
flask db upgrade
4. (Ít dùng) flask db downgrade base
Nếu bạn chỉ muốn xóa bỏ tất cả các thay đổi đã migrate mà KHÔNG xóa database, thì có thể dùng:
bash
flask db downgrade base
Nhưng cách này chỉ đưa schema về trạng thái trắng, không xóa data/database.
