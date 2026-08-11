# FieldTrack

A Linear-like ticket tracker used for internal engineering interviews and drills.

## Stack

- **Backend** — FastAPI + SQLAlchemy (`backend/`)
- **Frontend** — Next.js App Router (`web/`)
- **Tests** — pytest happy-path suite (`tests/`)

## Quick start

```bash
# API
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# Web
cd web
npm install
npm run dev
```

```bash
# Tests
pytest
```

## Layout

```
backend/
  main.py
  models.py
  schemas.py
  deps.py
  db.py
  cache.py
  routers/          # tickets, comments, users, auth
web/
  app/              # pages + api routes
  components/
  lib/
tests/
```
