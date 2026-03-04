# Test Data Hub

A Test Data Management System for generating synthetic data in enterprise workflows. AI-powered synthetic data generation and validation for financial/banking applications (credit card systems, business rules, test scenarios).

---

## Prerequisites

- **Python 3.8+** — `python --version`
- **Node.js 16+** and npm — `node --version`, `npm --version`
- **OpenAI API Key** — required for AI features
- **Git** — for cloning

---

## Quick Start (Local)

### 1. Backend

```bash
cd test_data_hub_backend-main
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in `test_data_hub_backend-main` (copy from `.env.example`):

```env
OPENAI_API_KEY=your-actual-openai-api-key-here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

Start backend:

```bash
python start_backend.py
```

- API docs: http://localhost:8000/docs  
- WebSocket: ws://localhost:8000/ws/logs  
- Health: http://localhost:8000/health  

### 2. Frontend

In a **new terminal**:

```bash
cd test_data_hub_frontend-main
npm install
```

Optional `.env` in `test_data_hub_frontend-main`:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_APP_ENVIRONMENT=development
```

Start frontend:

```bash
npm start
```

App: http://localhost:3000  

---

## Project Structure

```
Test-Data-Hub/
├── test_data_hub_backend-main/    # FastAPI backend
│   ├── input_schemas/             # Schema CSV files
│   ├── business_logic_library/    # Business rules & test scenarios
│   ├── runs/                      # Per-run outputs (timestamped folders)
│   ├── main.py, start_backend.py
│   ├── schema_analyzer_agent.py
│   ├── synthetic_data_generator_agent.py
│   ├── validation_agent.py
│   ├── test_scenario_data_generator_agent.py
│   └── run_complete_pipeline.py  # Full pipeline orchestrator
└── test_data_hub_frontend-main/  # React + TypeScript + Tailwind
    ├── src/pages/                # App pages (Home, Data Source, Schema, etc.)
    ├── src/services/apiService.ts
    └── package.json
```

---

## Backend: Two User Journeys

### 1. Synthetic Data Generation (schema-only → full pipeline)

- **Input:** Schema files in `input_schemas/`
- **Flow:** Schema analysis → Synthetic data generation → Validation → (optional) Test scenario generation
- **Use when:** You have schemas but no data; you want test data from scratch.

### 2. Functional Test Scenario Generation (data + schema → business logic → test scenarios)

- **Input:** Schemas + existing data in `runs/{run_id}/input_data/`
- **Flow:** Schema analysis → Business logic from data → Test scenario generation → Validation
- **Use when:** You have existing data and want business rules and test scenarios.

**Run full pipeline:**

```bash
cd test_data_hub_backend-main
python run_complete_pipeline.py
# Choose journey (1 or 2) and follow prompts
```

**Run agents individually:**

```bash
python schema_analyzer_agent.py
python synthetic_data_generator_agent.py
python business_logic_library/library_generator_agent.py
python validation_agent.py
python test_scenario_data_generator_agent.py
```

---

## Backend: Key Components

| Component | Purpose |
|-----------|--------|
| **Schema Analyzer** | Analyzes CSV schemas; full mode (with test scenarios) or schema-only mode |
| **Synthetic Data Generator** | Generates realistic data from schema analysis; dependency order, business rules |
| **Business Logic Library Generator** | Data analysis mode or interactive chat; produces rules and test scenarios |
| **Validation Agent** | Validates data vs business rules and scenarios; outputs reports in `runs/{run_id}/validation/` |
| **Test Scenario Data Generator** | Adds test data for selected scenarios; keeps referential integrity |

**Data model (5 core tables):** `customer_info`, `credit_card_products`, `credit_card_accounts`, `credit_card_transactions`, `imobile_user_session`.

---

## Frontend: Features

- Windows-style UI (React + TypeScript + Tailwind)
- Multi-page flow: data source → schema analysis → data generation → destination
- Real-time logs and progress via WebSocket
- REST API and WebSocket integration with backend

---

## Deployment

### Backend (e.g. Render)

- **Build:** `pip install -r requirements.txt`
- **Start:** `python start_backend.py`
- **Env:** Set `ENVIRONMENT=production`, `ALLOWED_ORIGINS=https://your-frontend-domain.com`, plus `OPENAI_API_KEY` and any DB vars. Never commit `.env`.

### Frontend (e.g. Render Static Site)

- **Build:** `npm install && npm run build`
- **Publish directory:** `build`
- **Env:** `REACT_APP_API_BASE_URL`, `REACT_APP_WS_URL` (use production backend URL; `https`/`wss` in production).

### CORS

Backend must allow the frontend origin. Set `ALLOWED_ORIGINS` in backend `.env` (or deployment env) to a comma-separated list, e.g.:

- Development: `http://localhost:3000`, `http://localhost:3001`
- Production: `https://your-app.onrender.com`, `https://your-custom-domain.com`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Backend `OPENAI_API_KEY` error | Ensure `.env` exists in backend root with valid key |
| Port 8000 in use | Change `PORT` in backend `.env` or stop process using 8000 |
| Frontend can’t reach backend | Backend running? Correct `REACT_APP_API_BASE_URL`? Backend `ALLOWED_ORIGINS` includes frontend URL? |
| Port 3000 in use | Use different port (e.g. 3001) or set `PORT=3001` in frontend `.env` |
| `npm install` / build fails | `npm cache clean --force`, remove `node_modules` and `package-lock.json`, then `npm install` |

---

## Security

- **Do not commit `.env`** — use `.env.example` as a template only.
- Keep **OpenAI API key** and DB credentials in environment variables.
- In production, set env vars in the deployment platform (e.g. Render).
- Restrict **CORS** to your frontend domain(s) in production.

---

## License

For internal use in test data generation for financial applications.
