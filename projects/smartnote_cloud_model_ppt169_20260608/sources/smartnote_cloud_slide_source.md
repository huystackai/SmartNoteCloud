# SmartNoteCloud / MindDeckNote Lite Cloud Report Slide Source

## Project summary

MindDeckNote Lite is a cloud-native demo web app for Cloud Computing. It supports user registration/login, block-based note editing, AI note summarization, flashcard generation, flashcard review, and a small dashboard.

## Runtime architecture

User Browser -> Nginx Reverse Proxy -> React Frontend Container / FastAPI Backend Container -> PostgreSQL Container.

When AI is needed, FastAPI calls Mimo Xiaomi AI API over HTTPS.

Nginx is the single public entrypoint. Web requests go to the frontend. `/api/...` requests go to FastAPI. PostgreSQL stays private inside Docker network and is not publicly exposed.

## Deployment process

1. User accesses `https://pkiresearch.id.vn`.
2. DNS points domain to AWS EC2.
3. Nginx receives HTTPS traffic and routes requests.
4. React frontend renders the note/flashcard interface.
5. FastAPI validates JWT and handles notes, blocks, flashcards, reviews, and dashboard API.
6. FastAPI reads/writes PostgreSQL.
7. For AI features, FastAPI calls external Mimo AI API.
8. Docker Compose runs all internal app services on EC2.

## Cloud service model mapping

- IaaS: AWS EC2. AWS provides virtual machine, CPU, RAM, disk, networking, and security group. The team installs Docker, configures Nginx, runs containers, manages SSL, and operates the app.
- PaaS: Elastic Beanstalk would be the PaaS alternative. AWS would manage platform deployment, runtime, health checks, scaling hooks, and more infrastructure automation. The current project mentions this as the next abstraction layer if deployment is upgraded.
- SaaS / API Service: Mimo Xiaomi AI API. The app consumes ready-made AI capability through a REST API. The team does not manage model hosting, GPU, or inference platform.

## Security notes

- Passwords are hashed with bcrypt.
- Login returns JWT.
- Protected APIs require `Authorization: Bearer <token>`.
- API keys stay in `.env`, not source code.
- PostgreSQL is private; for DBeaver it is reachable only through SSH tunnel.
- Nginx is the public entrypoint with HTTPS and security headers.

## One-slide goal

Create one 16:9 report slide that clearly shows the end-to-end request/deployment flow and labels which parts are IaaS, PaaS, and SaaS. The slide should be useful for a Cloud Computing oral presentation.
