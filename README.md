# FinGuard 🛡️ — Real-Time AML Transaction Graph Analyser

FinGuard is a high-performance, real-time Anti-Money Laundering (AML) transaction monitoring and graph analysis system. By combining traditional rule-based velocity metrics with machine learning anomaly detection and Graph ML, FinGuard ingests, analyzes, and scores financial transactions dynamically to uncover sophisticated financial crime typologies.

---

## 🚀 Key Features

* **Real-Time Ingestion & Scoring:** Asynchronous REST endpoints capable of scoring transactions with low-latency overhead[cite: 5, 10].
* **Hybrid AI Scoring Architecture:** Combines Isolation Forest (outlier detection), Autoencoders (reconstruction thresholds), and statistical ensembles to flag suspicious activity[cite: 1, 10].
* **Graph-Based Typology Detection:** Live NetworkX-backed analysis to catch complex structures such as circular looping networks, structuring under reporting limits, and illicit cross-border money flows[cite: 6, 8, 10].
* **WebSocket Stream Feed:** Real-time push updates via WebSockets (`/ws/live`) to drive dynamic dashboards.
* **Containerized Architecture:** Fully dockerized ecosystem containing the FastAPI application, MongoDB persistent storage, and a Redis caching/streaming layer[cite: 3, 4].

---

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI, Uvicorn[cite: 6]
* **Databases & Streaming:** MongoDB (via Motor Async Driver), Redis[cite: 6]
* **Data Science & AI:** PyTorch, Scikit-Learn, NumPy[cite: 6]
* **Graph Networking:** NetworkX[cite: 6]
* **Testing Framework:** Pytest, Pytest-Asyncio[cite: 6]

---

## 📂 Project Structure

```text
finguard/
│
├── ai_engine/                 # Machine Learning & AI Inference Pipeline
│   ├── features/              # Feature engineering (e.g., VelocityMatrix)
│   ├── models/                # ML Models (e.g., EnsembleScorer)
│   └── inference.py           # Core AMLInferenceEngine class
│
├── backend/                   # FastAPI Web Server Application
│   ├── services/              # Business logic & graph builder integrations
│   └── main.py                # App entrypoint and API routers
│
├── tests/                     # Automated Test Suites
│   ├── test_aml_patterns.py   # Integration tests for AML typologies
│   ├── test_graph.py          # Unit tests for graph builder payloads
│   └── test_inference.py      # Unit tests for ML models and feature shapes
│
├── Dockerfile                 # Docker container build rules
├── docker-compose.yml         # Local orchestration for App, MongoDB, and Redis
├── requirements.txt           # Explicit Python dependencies framework
└── .env.example               # Template configuration environment keys

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




## autor
Rabbani Holi
