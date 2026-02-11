# 🔥 InsightForge

**A production-grade, multi-user data analysis platform powered by natural language AI.**

Upload any dataset. Ask questions in plain English. Get instant answers, visualizations, and insights — no SQL required.

### 🌐 [Try the Live Demo](https://insight-forge-ui-production.up.railway.app) — no setup required

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql&logoColor=white)
![Multi-LLM](https://img.shields.io/badge/Multi--LLM-Claude_|_OpenAI-ff6b35)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🎯 The Problem

Data teams waste hours writing SQL queries, cleaning exports, and building one-off visualizations. Non-technical stakeholders can't self-serve on data without engineering help. The gap between "I have data" and "I have answers" is too wide.

## 💡 The Solution

InsightForge bridges that gap. Upload your data in any format, ask questions in plain English, and get:
- **Instant query results** — AI translates natural language → SQL/Pandas
- **Context-aware answers** — upload a context file so the AI understands your data like your team does
- **Smart visualizations** — AI suggests the best chart type for your data
- **Multi-user isolation** — every user's datasets and queries are scoped and secure
- **Bring Your Own Key** — use your own Claude or OpenAI API key, or fall back to the server default
- **Export anywhere** — Tableau integration, Plotly charts, or raw data export

---

## 🆕 What's New: Bring Your Own API Key (BYOK)

InsightForge now supports **multi-provider LLM integration** with a BYOK model:

- **🔑 Use your own key** — Enter your Anthropic Claude or OpenAI API key directly in the UI
- **🔄 Fallback to server default** — No key? No problem. The platform falls back to the server-configured default key
- **🤖 Multi-provider support** — Switch between Claude and OpenAI based on your preference or use case
- **🔒 Secure key handling** — User API keys are handled securely per-session, never exposed in logs or responses

### Why BYOK?

| Use Case | How BYOK Helps |
|---|---|
| **Teams with existing API contracts** | Use your org's negotiated API key and rate limits |
| **Cost control** | Each user tracks their own API usage and billing |
| **Model comparison** | Run the same query through Claude and OpenAI to compare results |
| **Self-hosted deployments** | Deploy InsightForge without needing a shared API key |
| **Demos & trials** | New users can try the platform with the server default key |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│              React + TypeScript + Vite + Tailwind           │
│     ┌──────────┐  ┌───────────┐  ┌──────────────────┐       │
│     │ Data     │  │ Query     │  │ Visualization    │       │
│     │ Upload   │  │ Interface │  │ Dashboard        │       │
│     └──────────┘  └───────────┘  └──────────────────┘       │
│                        │                                    │
│              ┌─────────┴─────────┐                          │
│              │  BYOK Key Manager │                          │
│              │  (Claude/OpenAI)  │                          │
│              └───────────────────┘                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JWT Auth)
┌─────────────────────────┴───────────────────────────────────┐
│                         BACKEND                             │
│                    FastAPI + SQLAlchemy                     │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐      │
│  │ Auth     │  │ Data         │  │ Query Engine      │      │
│  │ Service  │  │ Ingestion    │  │ (SQL/Pandas/NL)   │      │
│  │ (JWT)    │  │ Service      │  │                   │      │
│  └──────────┘  └──────────────┘  └────────┬──────────┘      │
│                                           │                 │
│  ┌──────────┐  ┌──────────────┐  ┌────────┴──────────┐      │
│  │ File     │  │ Viz          │  │ LLM Provider      │      │
│  │ Parser   │  │ Generator    │  │ Router (BYOK)     │      │
│  │ Engine   │  │ (Plotly)     │  │ Claude │ OpenAI   │      │
│  └──────────┘  └──────────────┘  └───────────────────┘      │
│                                                             │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
    ┌──────┴──────┐               ┌───────┴───────┐
    │ PostgreSQL  │               │    Redis      │
    │ (Users,     │               │  (Query Cache,│
    │  Datasets,  │               │   Sessions)   │
    │  Queries)   │               │               │
    └─────────────┘               └───────────────┘
```

---

## ✨ Key Features

### 📥 Multi-Format Data Ingestion
- **File Upload**: CSV, JSON, Excel (.xlsx), Parquet
- **URL Import**: Fetch datasets from any public URL
- **Web Scraping**: Extract tables from web pages automatically
- Schema detection, type inference, and data profiling on upload

### 🧠 AI-Powered Natural Language Queries
- Ask questions like *"What are the top 5 products by revenue?"*
- AI translates to optimized SQL or Pandas operations
- Supports SQL, Pandas-style filtering, and plain English — all from one interface
- Query history and result caching for performance

### 📄 Context File Support
- Upload a context file alongside your data to describe what columns mean, business rules, and data relationships
- InsightForge injects this context into every AI prompt for dramatically better accuracy
- Optional — works without one, but transforms answer quality with one
- Think of it as giving the AI the same tribal knowledge a new engineer would need

### 🔑 Bring Your Own API Key (BYOK)
- Use your own Anthropic Claude or OpenAI API key
- Seamless fallback to server-configured default
- Switch providers per query based on preference
- Secure handling — keys never logged or persisted beyond session

### 📊 Smart Visualizations
- **AI-Suggested Charts**: Analyzes your data types and recommends optimal visualizations
- **Interactive Plotly Charts**: Bar, line, scatter, heatmap, and more
- Saved visualizations per user

### 🔒 Multi-User Architecture
- JWT authentication with secure token refresh
- User-scoped datasets — complete tenant isolation
- Role-based access patterns
- bcrypt password hashing

### 🐳 Production-Ready
- Docker Compose for local and production environments
- PostgreSQL for persistent storage, Redis for caching
- Environment-based configuration
- Comprehensive test suite

---

## 🛠️ Tech Stack

| Layer | Technology | Why This Choice |
|---|---|---|
| **Frontend** | React 18 + TypeScript + Vite + TailwindCSS | Type-safe, fast HMR, utility-first styling |
| **Backend** | FastAPI + SQLAlchemy + Pydantic | Async-first, auto-generated OpenAPI docs, validation |
| **Database** | PostgreSQL 14+ | ACID compliance, JSON support, production-proven |
| **Cache** | Redis | Sub-ms query caching, session storage |
| **Data Processing** | Pandas + NumPy + pandasql | Industry-standard data manipulation |
| **Visualization** | Plotly + Matplotlib | Interactive charts with export capability |
| **AI/LLM** | Anthropic Claude + OpenAI (BYOK) | Multi-provider support with user-level key management |
| **Auth** | JWT + bcrypt | Stateless auth with secure password hashing |
| **Infrastructure** | Docker + Docker Compose | Consistent dev/prod environments |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

### Quick Start with Docker

```bash
git clone https://github.com/pallavi-chandrashekar/insight-forge.git
cd insight-forge
cp .env.example .env
# Edit .env with your API keys and database credentials
docker-compose up
```

The app will be available at `http://localhost:5173` with the API at `http://localhost:8000`.

### Manual Setup

<details>
<summary><strong>Backend Setup</strong></summary>

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn app.main:app --reload
```

API available at `http://localhost:8000` | Docs at `http://localhost:8000/docs`
</details>

<details>
<summary><strong>Frontend Setup</strong></summary>

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:5173`
</details>

### Using BYOK

1. **With your own key**: Navigate to Settings in the UI → enter your Anthropic or OpenAI API key → all queries will use your key
2. **Without a key**: The platform automatically falls back to the server-configured default API key
3. **Switching providers**: Select your preferred LLM provider per session — compare Claude vs OpenAI results on the same data

---

## 📁 Project Structure

```
insight-forge/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # REST API endpoints (auth, datasets, query, viz)
│   │   ├── core/             # Config, database setup, security
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic layer (incl. LLM provider routing)
│   │   └── main.py           # FastAPI application entry
│   ├── tests/                # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components (incl. API key manager)
│   │   ├── pages/            # Page-level components
│   │   ├── services/         # API client layer
│   │   ├── store/            # State management
│   │   ├── hooks/            # Custom React hooks
│   │   └── utils/            # Shared utilities
│   └── Dockerfile
├── docs/                     # Documentation
├── docker-compose.yml        # Development environment
├── docker-compose.prod.yml   # Production environment
└── README.md
```

---

## 🔌 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create new account |
| `POST` | `/api/auth/login` | Login and get JWT tokens |
| `POST` | `/api/auth/refresh` | Refresh access token |
| `GET` | `/api/auth/me` | Get current user profile |

### Datasets
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/datasets/upload` | Upload a data file (CSV, JSON, Excel, Parquet) |
| `POST` | `/api/datasets/from-url` | Import dataset from URL |
| `POST` | `/api/datasets/scrape` | Scrape table from web page |
| `GET` | `/api/datasets` | List all user datasets |
| `GET` | `/api/datasets/{id}` | Get dataset details + schema |
| `GET` | `/api/datasets/{id}/preview` | Preview first N rows |
| `DELETE` | `/api/datasets/{id}` | Delete dataset |

### Query Engine
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query/execute` | Execute SQL or Pandas query |
| `POST` | `/api/query/natural-language` | Natural language → results (supports BYOK) |
| `GET` | `/api/query/history` | User's query history |

### Visualization
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/visualize/generate` | Generate chart from query results |
| `POST` | `/api/visualize/suggest` | AI-powered chart suggestions (supports BYOK) |
| `GET` | `/api/visualize` | List saved visualizations |

---

## 💻 Usage Example

```python
import requests

# 1. Authenticate
response = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Upload a dataset
with open("sales_data.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/datasets/upload",
        headers=headers,
        files={"file": f},
        data={"name": "Q4 Sales"}
    )
dataset_id = response.json()["id"]

# 3. Ask a question in plain English (uses BYOK key if configured)
response = requests.post(
    "http://localhost:8000/api/query/natural-language",
    headers=headers,
    json={
        "dataset_id": dataset_id,
        "question": "What are the top 5 products by revenue?"
    }
)
print(response.json()["result_preview"])

# 4. Get AI-suggested visualizations
response = requests.post(
    "http://localhost:8000/api/visualize/suggest",
    headers=headers,
    json={"dataset_id": dataset_id}
)
for chart in response.json():
    print(f"{chart['chart_type']}: {chart['title']}")
```

---

## ⚙️ Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT signing key | ✅ |
| `API_KEY` | Default Claude API key (fallback for BYOK) | ✅ |
| `OPENAI_API_KEY` | Default OpenAI API key (fallback for BYOK) | Optional |
| `CORS_ORIGINS` | Allowed frontend origins | ✅ |
| `REDIS_URL` | Redis connection string | Optional |
| `TABLEAU_PUBLIC_ENABLED` | Enable Tableau export | Optional |

---

## 🧪 Development

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Code style
# Backend: Black, isort, flake8
# Frontend: ESLint, Prettier
```

---

## 🗺️ Roadmap

- [x] Multi-format data ingestion (CSV, JSON, Excel, Parquet)
- [x] Natural language queries powered by AI
- [x] AI-suggested visualizations
- [x] Multi-user authentication and dataset isolation
- [x] Bring Your Own API Key (BYOK) with multi-provider support**
- [ ] Real-time collaborative querying
- [ ] Scheduled data refresh from URLs
- [ ] Custom dashboard builder
- [ ] Export to Google Sheets
- [ ] Support for database connections (MySQL, MongoDB)
- [ ] Role-based access control (Admin, Viewer, Editor)

---

## 📝 Design Decisions

| Decision | Rationale |
|---|---|
| **FastAPI over Django** | Async-first, auto OpenAPI docs, better for API-only backends |
| **Multi-provider LLM (BYOK)** | Users control costs, compare models, use org API contracts |
| **Provider fallback pattern** | Zero-friction onboarding — works out of the box with server default |
| **Pandas + pandasql** | Flexibility to handle both SQL and programmatic queries |
| **User-scoped isolation** | Every query runs against user's own datasets — no cross-tenant leakage |
| **Redis caching** | Identical NL queries return cached results in <10ms |

---

## 👤 Author

**Pallavi Chandrashekar**
- [LinkedIn](https://linkedin.com/in/pchandrashekar/)
- [GitHub](https://github.com/pallavi-chandrashekar)

Lead Software Engineer with 9+ years of experience building distributed data systems, multi-tenant pipelines, and AI-powered platforms at scale.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.