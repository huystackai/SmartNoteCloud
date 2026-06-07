# MindDeckNote Lite Architecture

## Tong Quan

```text
Browser
  |
  v
Nginx Reverse Proxy :80
  |
  +--> React Frontend Container
  |
  +--> FastAPI Backend Container
          |
          +--> PostgreSQL Container
          |
          +--> Mimo Xiaomi AI API
```

MindDeckNote Lite la mot ung dung cloud-native mini. Moi thanh phan chay trong container rieng va giao tiep qua Docker network. Ben ngoai chi truy cap Nginx port 80.

## Components

- `nginx`: reverse proxy, route `/api` den backend va `/` den frontend.
- `frontend`: React + Vite static build, serve bang Nginx nho trong container.
- `backend`: FastAPI, JWT auth, note/page/block API, flashcard/review API va AI integration.
- `db`: PostgreSQL 16 voi persistent volume.
- `Mimo API`: external AI API dung cho summarize va generate flashcards.

## Request Flow

1. User truy cap `http://PUBLIC_IP`.
2. Nginx nhan request.
3. UI request duoc proxy den frontend container.
4. API request duoc proxy den backend container.
5. Backend verify JWT va xu ly request.
6. Backend doc/ghi PostgreSQL.
7. Khi goi AI, backend gui HTTPS request den Mimo API.

## Security

- Password hash bang bcrypt.
- Login tra JWT access token.
- API protected yeu cau `Authorization: Bearer TOKEN`.
- API key nam trong `.env`, khong hardcode trong source.
- Database port khong expose public.
- Nginx la public entrypoint duy nhat.
- Pydantic validate body va query.

## Database

```text
users 1..n workspaces
workspaces 1..n pages
pages 1..n blocks
workspaces 1..n decks
decks 1..n cards
cards 1..n card_reviews
```

Flashcard review dung SM-2 Lite:

- Again: reset repetition, due lai som.
- Hard: tang cham.
- Good: tang repetition binh thuong.
- Easy: tang ease va interval nhanh hon.

## Cloud Concepts Mapping

- EC2 la IaaS vi cung cap may ao va ha tang. Nguoi dung tu cai Docker, deploy va quan ly runtime.
- Docker la containerization vi dong goi app va dependency thanh image doc lap.
- Mimo AI API la SaaS/API Service vi ung dung dung dich vu AI co san qua REST API.
- Elastic Beanstalk se la PaaS neu dung de AWS quan ly deployment platform.
