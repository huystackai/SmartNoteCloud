# MindDeckNote Lite

MindDeckNote Lite la web app ghi chu AI va flashcards cho mon Cloud Computing. Ban Lite tap trung vao kien truc cloud-native vua du demo: React frontend, FastAPI backend, PostgreSQL, Nginx reverse proxy, Docker Compose tren AWS EC2 va tich hop Mimo Xiaomi API.

## 1. Kien Truc Tong The

```text
User Browser
    |
    v
Nginx Reverse Proxy :80
    |
    +--> Frontend Container: React + Vite static build
    |
    +--> Backend Container: FastAPI REST API
              |
              +--> PostgreSQL Container
              |
              +--> External AI API: Mimo Xiaomi API
```

Nginx la entrypoint public. Request `/` di den frontend, request `/api/...` di den FastAPI. Backend validate JWT, thao tac PostgreSQL va goi Mimo API qua HTTPS. PostgreSQL chi nam trong Docker network, khong expose public port.

## 2. Chuc Nang

- Auth: register, login, JWT, logout.
- Notes: workspace mac dinh, page, block editor, search noi dung.
- AI: summarize note, generate flashcards tu note.
- Flashcards: deck, card, due cards, review Again/Hard/Good/Easy.
- Dashboard nho: so notes, cards, due cards, studied today.

## 3. Cau Truc Thu Muc

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
├── nginx/nginx.conf
├── docker-compose.yml
├── .env.example
└── docs/
```

## 4. Database Schema

Core tables:

- `users`: username, email, password_hash, created_at.
- `workspaces`: personal workspace cua user.
- `pages`: note page, title, summary.
- `blocks`: paragraph, heading, list, quote, code.
- `decks`: flashcard deck.
- `cards`: front, back, source_text, ease, interval, repetition, due_at.
- `card_reviews`: lich su review theo SM-2 Lite.

Alembic migrations:

- `0001_initial_schema.py`: users va bang tasks cu, giu tu ban dau de migration lien mach.
- `0002_minddeck_lite_schema.py`: schema MindDeckNote Lite.

## 5. Backend API Chinh

```text
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

GET    /api/mind/bootstrap
GET    /api/mind/pages
POST   /api/mind/pages
GET    /api/mind/pages/{page_id}
PATCH  /api/mind/pages/{page_id}
PUT    /api/mind/pages/{page_id}/blocks

POST   /api/mind/pages/{page_id}/summarize
POST   /api/mind/pages/{page_id}/generate-cards

GET    /api/mind/decks
GET    /api/mind/decks/{deck_id}/cards?due=true
POST   /api/mind/cards
POST   /api/mind/reviews
GET    /api/mind/stats
GET    /api/mind/search?q=...

GET    /health
```

## 6. Local Setup

```bash
cp .env.example .env
```

Sua cac bien quan trong:

```env
POSTGRES_DB=minddecknote
POSTGRES_USER=minddeck
POSTGRES_PASSWORD=your_strong_password
DATABASE_URL=postgresql+psycopg2://minddeck:your_strong_password@db:5432/minddecknote
JWT_SECRET_KEY=your_long_random_secret
MIMO_API_URL=https://your-mimo-endpoint/v1
MIMO_API_KEY=your_api_key
MIMO_MODEL=your_model
```

Chay app:

```bash
docker compose up -d --build
docker compose ps
curl http://localhost/health
```

Mo browser:

```text
http://localhost
```

Dung app:

```bash
docker compose down
```

Xoa database volume khi can reset demo:

```bash
docker compose down -v
```

## 7. Deploy AWS EC2 Amazon Linux 2023

Tao EC2:

- AMI: Amazon Linux 2023.
- Instance type: `t3.small` de build Docker de hon, `t3.micro` van co the demo nhe.
- Security Group:
  - SSH 22 tu IP cua ban.
  - HTTP 80 tu `0.0.0.0/0`.
  - HTTPS 443 neu cau hinh domain/SSL.

SSH:

```bash
chmod 400 notesmart.pem
ssh -i notesmart.pem ec2-user@PUBLIC_IP
```

Cai Docker va Compose:

```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
sudo usermod -aG docker ec2-user
```

Khuyen nghi tao swap cho may nho:

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

## 8. Cloud Concepts

- EC2 la IaaS: AWS cap may ao, CPU, RAM, disk, network. Minh tu cai Docker, cau hinh app va van hanh container.
- Docker la containerization: moi thanh phan duoc dong goi thanh image rieng, chay nhat quan giua local va EC2.
- Mimo AI API la SaaS/API Service: app chi goi REST API bang key, khong quan ly model, GPU hay inference server.
- Elastic Beanstalk se la PaaS neu dung: AWS quan ly platform deployment va health check nhieu hon.

## 9. Troubleshooting

Backend restart:

```bash
docker compose logs --tail=120 backend
```

Nginx 502:

```bash
docker compose ps
curl http://localhost/health
```

AI loi:

```bash
docker compose logs --tail=100 backend
```

Kiem tra `.env` co `MIMO_API_URL`, `MIMO_API_KEY`, `MIMO_MODEL`.

Database:

```bash
docker compose exec db psql -U minddeck -d minddecknote
\dt
select count(*) from users;
select count(*) from pages;
```
