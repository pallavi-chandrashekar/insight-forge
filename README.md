# InsightForge

A multi-user data analysis platform that enables natural language queries, automated visualizations, and seamless data exploration.

## Features

- **Multi-format Data Import**: Upload CSV, JSON, Excel, or Parquet files, fetch from URLs, or scrape web tables
- **Natural Language Queries**: Ask questions in plain English and get results powered by Claude AI
- **Multiple Query Types**: SQL, Pandas-style filtering, and natural language all supported
- **Auto-suggested Visualizations**: AI recommends the best charts based on your data types
- **Tableau Integration**: Export to Tableau when credentials are provided, or use built-in Plotly charts
- **Multi-user Support**: Secure authentication with user-scoped datasets

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite + TailwindCSS |
| Backend | FastAPI + SQLAlchemy + Pydantic |
| Database | PostgreSQL + Redis |
| Data Processing | Pandas + NumPy + pandasql |
| Visualization | Plotly + Matplotlib |
| LLM | Anthropic Claude API |
| Auth | JWT + bcrypt |

## Project Structure

```
insight-forge/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── core/             # Config, database setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI application
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   ├── store/            # State management
│   │   ├── hooks/            # Custom hooks
│   │   └── utils/            # Utilities
│   └── public/
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `API_KEY` | Claude API key for NL queries | Yes |
| `CORS_ORIGINS` | Allowed frontend origins | Yes |
| `REDIS_URL` | Redis connection (optional) | No |
| `TABLEAU_PUBLIC_ENABLED` | Enable Tableau export | No |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Datasets
- `POST /api/datasets/upload` - Upload a data file
- `POST /api/datasets/from-url` - Import from URL
- `POST /api/datasets/scrape` - Scrape web table
- `GET /api/datasets` - List user datasets
- `GET /api/datasets/{id}` - Get dataset details
- `GET /api/datasets/{id}/preview` - Preview dataset rows
- `DELETE /api/datasets/{id}` - Delete dataset

### Query
- `POST /api/query/execute` - Execute SQL or Pandas query
- `POST /api/query/natural-language` - Natural language query
- `GET /api/query/history` - Query history

### Visualization
- `POST /api/visualize/generate` - Generate chart
- `POST /api/visualize/suggest` - Get AI chart suggestions
- `GET /api/visualize` - List saved visualizations

## Usage Examples

### Upload and Query Data

```python
import requests

# Login
response = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Upload CSV
with open("sales_data.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/datasets/upload",
        headers=headers,
        files={"file": f},
        data={"name": "Sales Data"}
    )
dataset_id = response.json()["id"]

# Natural language query
response = requests.post(
    "http://localhost:8000/api/query/natural-language",
    headers=headers,
    json={
        "dataset_id": dataset_id,
        "question": "What are the top 5 products by revenue?"
    }
)
print(response.json()["result_preview"])
```

### Get Visualization Suggestions

```python
response = requests.post(
    "http://localhost:8000/api/visualize/suggest",
    headers=headers,
    json={"dataset_id": dataset_id}
)
suggestions = response.json()
for suggestion in suggestions:
    print(f"{suggestion['chart_type']}: {suggestion['title']}")
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

- Backend: Black, isort, flake8
- Frontend: ESLint, Prettier

## License

MIT License
