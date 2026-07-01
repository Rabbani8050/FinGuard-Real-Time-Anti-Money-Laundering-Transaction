# FinGuard — Real-Time AML Transaction Graph Analyser

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server (no Mongo/Redis needed — falls back gracefully)
cd finguard
uvicorn backend.main:app --reload

# Open dashboard
open http://localhost:8000

# API docs
open http://localhost:8000/docs
```

## Run Tests

```bash
cd finguard
pytest tests/ -v
```

## With Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/tx` | Ingest & score a transaction |
| GET | `/api/alerts` | Paginated alert list |
| GET | `/api/alerts/stats` | Risk level breakdown |
| GET | `/api/graph` | Account linkage graph |
| WS | `/ws/live` | Real-time scored transaction feed |
| GET | `/health` | Health check |
