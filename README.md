# Thiết kế hệ thống hạ tầng Cloud cơ bản và so sánh bảo mật VPC x VPS

Repository này triển khai một hệ thống web cloud cơ bản dùng làm minh họa cho đề tài: **"Thiết kế hệ thống hạ tầng Cloud cơ bản và so sánh bảo mật VPC x VPS"**.

Ứng dụng demo là **MindDeckNote Lite**: một web app ghi chú, flashcard và trợ lý AI. Hệ thống được đóng gói bằng Docker Compose, triển khai trên AWS EC2, có reverse proxy Nginx, backend FastAPI, database PostgreSQL và tích hợp AI API bên ngoài.

## 1. Mục tiêu đề tài

- Thiết kế một hạ tầng cloud cơ bản có đủ các thành phần frontend, backend, database, reverse proxy và dịch vụ AI bên ngoài.
- Minh họa cách triển khai ứng dụng trên máy chủ cloud theo mô hình IaaS.
- Áp dụng các cơ chế bảo mật cơ bản: xác thực người dùng, JWT, phân quyền admin, khóa tài khoản, chặn IP, HTTPS, tách network container và không public database.
- So sánh bảo mật giữa mô hình triển khai trong VPC và mô hình VPS độc lập.
- Đưa ra nhận xét về ưu điểm, hạn chế và tình huống nên dùng VPC hoặc VPS.

## 2. Tổng quan hệ thống

```text
User Browser
    |
    | HTTPS
    v
Nginx Reverse Proxy
    |
    +--> Frontend Container
    |       React + Vite static build
    |
    +--> Backend Container
            FastAPI REST API
            |
            +--> PostgreSQL Container
            |
            +--> External AI API
```

Nginx là entrypoint public của hệ thống. Request giao diện đi đến frontend, request `/api/...` đi đến backend FastAPI. Backend xử lý xác thực, nghiệp vụ ghi chú, flashcard, admin, AI chat và lưu dữ liệu vào PostgreSQL.

PostgreSQL chỉ chạy trong Docker network nội bộ, không expose trực tiếp ra Internet. Người dùng chỉ truy cập qua Nginx.

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ |
| --- | --- |
| Frontend | React, Vite, CSS |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| Reverse proxy | Nginx |
| Container | Docker, Docker Compose |
| Cloud compute | AWS EC2 |
| AI service | External AI API |
| Auth | JWT, password hashing |
| Admin security | Lock user, block IP, active user tracking |

## 4. Chức năng chính

- Đăng ký, đăng nhập, đăng xuất bằng JWT.
- Tạo workspace, note page và block editor.
- Tìm kiếm nội dung ghi chú.
- Tóm tắt note bằng AI.
- Sinh flashcards từ note.
- Review flashcards theo mức Again, Hard, Good, Easy.
- Chat AI trong app.
- Rule-based assistant cho các câu hỏi thường gặp về cloud, quota, Docker, EC2, SaaS.
- Giới hạn mỗi tài khoản tối đa 8 lượt hỏi AI.
- Sau khi AI trả lời, có thể tạo nhiều flashcards nhỏ từ từng ý trong câu trả lời.
- Admin dashboard: xem user, user đang hoạt động, IP truy cập, khóa tài khoản và chặn IP.

## 5. Cấu trúc thư mục

```text
.
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── auth/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── main.py
│   │   └── database.py
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── nginx/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 6. Database schema

Các bảng chính:

- `users`: tài khoản, email, password hash, quyền admin, trạng thái khóa.
- `user_ip_addresses`: lưu IP từng user đã truy cập.
- `blocked_ip_addresses`: danh sách IP bị chặn.
- `workspaces`: workspace của người dùng.
- `pages`: note page.
- `blocks`: nội dung note theo block.
- `decks`: bộ flashcards.
- `cards`: flashcards.
- `card_reviews`: lịch sử ôn tập.
- `ai_chat_messages`: lịch sử chat AI và quota hỏi.

Alembic migrations:

- `0001_initial_schema.py`: schema ban đầu.
- `0002_minddeck_lite_schema.py`: workspace, pages, blocks, decks, cards, reviews.
- `0003_admin_controls.py`: admin, khóa user, theo dõi IP, chặn IP.
- `0004_ai_chat_quota.py`: lịch sử chat AI và quota.

## 7. API chính

```text
GET    /health

POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

GET    /api/mind/bootstrap
GET    /api/mind/pages
POST   /api/mind/pages
GET    /api/mind/pages/{page_id}
PATCH  /api/mind/pages/{page_id}
DELETE /api/mind/pages/{page_id}
PUT    /api/mind/pages/{page_id}/blocks

POST   /api/mind/pages/{page_id}/summarize
POST   /api/mind/pages/{page_id}/generate-cards

GET    /api/mind/decks
POST   /api/mind/decks
GET    /api/mind/decks/{deck_id}/cards?due=true
POST   /api/mind/cards
POST   /api/mind/reviews
GET    /api/mind/stats
GET    /api/mind/search?q=...

GET    /api/ai/chat/history
POST   /api/ai/chat

GET    /api/admin/stats
GET    /api/admin/users
GET    /api/admin/ip-addresses
POST   /api/admin/users/{user_id}/lock
POST   /api/admin/users/{user_id}/unlock
POST   /api/admin/ip-blocks
DELETE /api/admin/ip-blocks/{ip_address}
```

## 8. Các mô hình cloud trong hệ thống

### IaaS

AWS EC2 là lớp IaaS. Cloud provider cấp máy ảo, CPU, RAM, disk, network. Nhóm tự cài Docker, cấu hình Nginx, deploy backend, frontend và database.

### PaaS

Nếu mở rộng, hệ thống có thể dùng các dịch vụ PaaS như AWS Elastic Beanstalk, App Runner hoặc managed database. Khi đó cloud provider quản lý nhiều hơn về platform, runtime, health check và deployment.

### SaaS

AI API bên ngoài là một dạng SaaS/API service. Ứng dụng chỉ gọi API qua HTTPS bằng API key, không tự vận hành model AI, GPU hoặc inference server.

## 9. Bảo mật đã áp dụng trong hệ thống demo

- HTTPS qua Nginx khi triển khai với domain.
- JWT cho các API cần đăng nhập.
- Password được hash, không lưu plain text.
- Backend kiểm tra trạng thái tài khoản trước khi xử lý request.
- Admin có thể khóa tài khoản vi phạm.
- Admin có thể chặn IP.
- Ghi nhận IP từng user để theo dõi truy cập.
- PostgreSQL không public trực tiếp ra Internet.
- Backend, frontend, database chạy trong Docker network riêng.
- Biến nhạy cảm như database password, JWT secret, AI API key đặt trong `.env`.
- AI chat có quota 8 lượt mỗi tài khoản để hạn chế lạm dụng.

## 10. So sánh bảo mật VPC với VPS

### Khái niệm

**VPC (Virtual Private Cloud)** là một mạng riêng ảo trong cloud provider. VPC cho phép chia subnet public/private, cấu hình route table, security group, network ACL, NAT gateway, VPN và peering. Trong VPC, nhiều tài nguyên như EC2, database, load balancer có thể được đặt trong các vùng mạng khác nhau.

**VPS (Virtual Private Server)** là một máy chủ ảo độc lập do nhà cung cấp cấp sẵn. Người dùng thường nhận một public IP, quyền SSH và tự cấu hình firewall, web server, database, backup, monitoring.

VPC và VPS không hoàn toàn cùng một lớp khái niệm. VPC là lớp mạng riêng ảo; VPS là một máy chủ ảo. Tuy nhiên trong thực tế triển khai, có thể so sánh mô hình hạ tầng cloud có VPC với mô hình thuê VPS đơn lẻ.

### Bảng so sánh

| Tiêu chí | VPC | VPS |
| --- | --- | --- |
| Mức cô lập mạng | Cao hơn, có mạng riêng logic cho từng project/account. | Thường là một máy ảo có public IP, cô lập chủ yếu ở mức hypervisor và firewall máy chủ. |
| Public/private subnet | Hỗ trợ chia subnet public và private rõ ràng. Database có thể đặt private subnet. | Thường không có subnet riêng nếu dùng VPS đơn lẻ. Database dễ bị đặt chung trên cùng máy hoặc expose sai cấu hình. |
| Kiểm soát inbound/outbound | Security Group, Network ACL, route table, NAT gateway. | Chủ yếu dùng firewall hệ điều hành như ufw, iptables hoặc firewall của nhà cung cấp. |
| Giảm bề mặt tấn công | Dễ ẩn backend/database trong private network, chỉ public load balancer hoặc reverse proxy. | Nếu cấu hình đơn giản, nhiều service nằm trên cùng một IP public, bề mặt tấn công lớn hơn. |
| Quản lý nhiều tầng ứng dụng | Phù hợp kiến trúc nhiều server: web, API, database, cache, private service. | Phù hợp app nhỏ hoặc demo đơn giản; tách nhiều tầng sẽ khó quản trị hơn. |
| Khả năng mở rộng bảo mật | Dễ thêm WAF, Load Balancer, private endpoint, VPN, bastion host, IAM. | Có thể thêm dịch vụ ngoài nhưng thường thủ công và phụ thuộc nhà cung cấp. |
| Logging và audit | Có thể tích hợp VPC Flow Logs, CloudTrail, CloudWatch. | Chủ yếu dựa vào log trên server hoặc dịch vụ monitoring tự cài. |
| Chống lỗi cấu hình database | Database private subnet giúp giảm nguy cơ public nhầm. | Nếu database chạy cùng VPS hoặc mở port public, rủi ro cao hơn. |
| Chi phí và độ phức tạp | Phức tạp hơn, có thể tốn thêm chi phí NAT, Load Balancer, logging. | Rẻ hơn, dễ bắt đầu, ít thành phần. |
| Phù hợp | Hệ thống cần tách lớp, bảo mật mạng, mở rộng và vận hành lâu dài. | Demo nhỏ, website cá nhân, prototype hoặc hệ thống ít thành phần. |

### Nhận xét bảo mật

VPC an toàn hơn khi hệ thống có nhiều thành phần và cần tách public/private network. Ví dụ: chỉ Nginx hoặc Load Balancer được public, còn backend và database nằm private. Cách này giảm rủi ro scan port, brute force database hoặc truy cập trái phép vào service nội bộ.

VPS vẫn có thể bảo mật tốt nếu cấu hình đúng: đóng port không cần thiết, dùng firewall, SSH key, fail2ban, cập nhật hệ điều hành, HTTPS, backup và monitoring. Tuy nhiên VPS đơn lẻ dễ bị lỗi cấu hình hơn vì nhiều service thường nằm chung trên một máy public.

Với đề tài này, EC2 triển khai Docker Compose là mô hình IaaS cơ bản. Nếu nâng cấp bảo mật theo hướng VPC đầy đủ, hệ thống nên tách:

- Public subnet: Nginx hoặc Load Balancer.
- Private subnet: backend, database.
- Security Group: chỉ mở 80/443 ra Internet, SSH giới hạn IP quản trị.
- Database: không có public IP.
- Bastion hoặc VPN: dùng cho quản trị nội bộ.
- VPC Flow Logs: ghi nhận traffic mạng để phục vụ audit.

## 11. Local setup

Tạo file môi trường:

```bash
cp .env.example .env
```

Cấu hình các biến quan trọng:

```env
POSTGRES_DB=minddecknote
POSTGRES_USER=minddeck
POSTGRES_PASSWORD=your_strong_password
DATABASE_URL=postgresql+psycopg2://minddeck:your_strong_password@db:5432/minddecknote

JWT_SECRET_KEY=your_long_random_secret

MIMO_API_URL=https://your-ai-endpoint/v1
MIMO_API_KEY=your_api_key
MIMO_MODEL=your_model
AI_CHAT_LIMIT=8
```

Chạy hệ thống:

```bash
docker compose up -d --build
docker compose ps
curl http://localhost/health
```

Mở trình duyệt:

```text
http://localhost
```

Dừng hệ thống:

```bash
docker compose down
```

Reset database volume khi cần:

```bash
docker compose down -v
```

## 12. Deploy AWS EC2

Gợi ý cấu hình EC2:

- AMI: Amazon Linux 2023.
- Instance type: `t3.small` để build Docker ổn định hơn.
- Security Group:
  - SSH 22 chỉ mở cho IP quản trị.
  - HTTP 80 mở public nếu cần redirect HTTPS.
  - HTTPS 443 mở public.
  - Không mở PostgreSQL ra Internet.

SSH:

```bash
chmod 400 notesmart.pem
ssh -i notesmart.pem ec2-user@PUBLIC_IP
```

Cài Docker:

```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
sudo usermod -aG docker ec2-user
```

Khuyến nghị tạo swap cho máy nhỏ:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Deploy:

```bash
git clone YOUR_REPO_URL minddecknote
cd minddecknote
cp .env.example .env
nano .env
docker compose up -d --build
```

Verify:

```bash
docker compose ps
curl http://localhost/health
curl http://PUBLIC_IP/health
docker compose logs --tail=100 backend
docker compose exec db psql -U minddeck -d minddecknote -c '\dt'
```

## 13. Hướng phát triển

- Tách database sang managed database trong private subnet.
- Đưa backend vào private subnet, chỉ cho Nginx hoặc Load Balancer gọi.
- Thêm WAF trước reverse proxy.
- Thêm rate limit theo IP ở Nginx hoặc backend.
- Thêm backup tự động cho PostgreSQL.
- Thêm monitoring và alerting.
- Thêm VPC Flow Logs để phân tích traffic.

## 14. Troubleshooting

Xem log backend:

```bash
docker compose logs --tail=120 backend
```

Kiểm tra Nginx 502:

```bash
docker compose ps
curl http://localhost/health
docker compose logs --tail=100 nginx
```

Kiểm tra AI:

```bash
docker compose logs --tail=100 backend
```

Kiểm tra `.env` có các biến:

```text
MIMO_API_URL
MIMO_API_KEY
MIMO_MODEL
AI_CHAT_LIMIT
```

Kiểm tra database:

```bash
docker compose exec db psql -U minddeck -d minddecknote
\dt
select count(*) from users;
select count(*) from pages;
select count(*) from cards;
select count(*) from ai_chat_messages;
```
