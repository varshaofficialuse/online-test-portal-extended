# Online Test Portal – Backend (FastAPI + MySQL)

## Quick Start
```bash
cp .env.example .env
docker compose up --build
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Useful
```bash
docker compose exec backend alembic revision --autogenerate -m "change"
docker compose exec backend alembic upgrade head
```
