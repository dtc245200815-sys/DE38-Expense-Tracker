# DE38 - Expense Tracker

## 1. Giới thiệu
Expense Tracker là hệ thống quản lý chi tiêu, hỗ trợ theo dõi thu nhập, chi phí và số dư thông qua giao diện web.

## 2. Công nghệ sử dụng
- Python Flask và Gunicorn
- PostgreSQL
- Docker và Docker Compose
- Nginx
- Prometheus và Grafana
- cAdvisor, PostgreSQL Exporter và Nginx Exporter
- Loki và Promtail

## 3. Kiến trúc hệ thống
- Nginx tiếp nhận yêu cầu HTTP và chuyển tiếp đến ứng dụng web.
- Ứng dụng Flask xử lý nghiệp vụ và kết nối PostgreSQL.
- Prometheus thu thập dữ liệu giám sát.
- Grafana hiển thị dashboard giám sát.
- Promtail thu thập log và gửi đến Loki để truy vấn.

## 4. Khởi chạy dự án
1. Cài đặt Docker Desktop.
2. Tạo file `.env` theo cấu hình môi trường cần thiết.
3. Mở terminal tại thư mục dự án.
4. Chạy:

```bash
docker compose up -d --build
```

5. Kiểm tra trạng thái dịch vụ:

```bash
docker compose ps
```

## 5. Các địa chỉ truy cập
- Website: http://localhost/
- Grafana: http://localhost:3000/
- Prometheus: http://localhost:9090/
- pgAdmin: http://localhost:5050/

Thông tin đăng nhập được cấu hình trong file `.env`.

## 6. Lưu ý bảo mật
- Không commit file `.env` hoặc thông tin bí mật lên GitHub.
- Không chia sẻ mật khẩu và khóa bí mật trong README.
- Các dịch vụ quản trị nên chỉ được truy cập trong môi trường phù hợp.

## 7. Repository
https://github.com/dtc245200815-sys/DE38-Expense-Tracker