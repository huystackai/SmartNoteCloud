# MindDeckNote Lite Presentation Guide

## Speaking Script

Chao thay co va cac ban. Hom nay em trinh bay MindDeckNote Lite, mot web app ghi chu AI va flashcards cho mon Cloud Computing.

Ung dung cho phep user dang ky, dang nhap, viet note theo block, dung AI de tom tat note, sinh flashcard va on tap theo spaced repetition. Muc tieu khong phai lam mot san pham enterprise, ma la demo ro cac thanh phan cloud-native co ban.

Kien truc gom Browser, Nginx reverse proxy, React frontend container, FastAPI backend container, PostgreSQL container va Mimo Xiaomi AI API. User truy cap public IP cua EC2. Nginx route giao dien den frontend va route `/api` den backend. Backend xu ly JWT, note, flashcard, review va luu du lieu vao PostgreSQL. Khi can AI, backend goi Mimo API qua HTTPS.

EC2 trong project nay la IaaS vi AWS cung cap may ao, CPU, RAM, disk va network. Em tu cai Docker, cau hinh app va van hanh container. Docker la containerization vi moi service duoc dong goi thanh image rieng va giao tiep qua Docker network. Mimo AI API la SaaS/API Service vi em chi su dung API co san, khong quan ly GPU hay model. Neu dung Elastic Beanstalk, khi do mo hinh se gan voi PaaS hon.

Ve security, password duoc hash bang bcrypt. Login tra JWT. PostgreSQL khong expose port public. API key nam trong `.env`. Chi Nginx mo port 80 ra Internet.

## Demo Flow

1. Mo `http://PUBLIC_IP`.
2. Register user moi.
3. Login vao workspace.
4. Xem note mau "Cloud Computing Project".
5. Them/sua block trong editor.
6. Bam Save.
7. Bam Summarize note de AI tao summary.
8. Bam Generate cards de AI sinh flashcards.
9. Bam Add de luu flashcards vao deck.
10. Review card bang Reveal answer va chon Again/Hard/Good/Easy.
11. Mo terminal chay `docker compose ps` va `curl /health`.
12. Show PostgreSQL tables bang `\dt`.

## Terminal Commands

```bash
docker compose ps
curl http://localhost/health
curl http://PUBLIC_IP/health
docker compose logs --tail=100 backend
docker compose exec db psql -U minddeck -d minddecknote -c '\dt'
```

## Expected AI Demo Input

Note content:

```text
Lam project Cloud Computing voi EC2, Docker, PostgreSQL, Nginx va AI API.
```

Expected flashcards:

```text
Q: EC2 thuoc mo hinh cloud nao?
A: EC2 la IaaS vi cung cap may ao va ha tang.

Q: Docker dung de lam gi?
A: Docker dong goi ung dung va dependency thanh container image.
```

## Cau Hoi Co The Gap

### Vi sao khong expose PostgreSQL?

Backend la service duy nhat can truy cap database. De database trong Docker network giup giam rui ro bi truy cap tu Internet.

### Vi sao can Nginx?

Nginx la entrypoint duy nhat, route frontend/backend va them security headers co ban.

### JWT co tac dung gi?

JWT giup backend xac thuc request API ma khong can luu session server-side cho demo nho.

### Alembic dung de lam gi?

Alembic versioning schema va tu chay migration khi backend container start.

### Neu scale thi nang cap gi?

Co the tach PostgreSQL sang Amazon RDS, them HTTPS voi domain, dung Load Balancer, dua secret vao AWS Secrets Manager va chay backend nhieu replica.
