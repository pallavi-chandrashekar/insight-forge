# InsightForge - Architecture Documentation

## System Overview

InsightForge is a multi-user data analysis platform built with a modern microservices-inspired architecture, featuring a React frontend, FastAPI backend, and PostgreSQL database.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client Layer                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      React Application                            │  │
│  │  • Vite Build Tool                                                │  │
│  │  • TypeScript for type safety                                     │  │
│  │  • TailwindCSS for styling                                        │  │
│  │  • State Management (Zustand/Redux)                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTPS/REST API
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API Gateway Layer                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Application                          │  │
│  │  • CORS Middleware                                                │  │
│  │  • JWT Authentication                                             │  │
│  │  • Request Validation (Pydantic)                                  │  │
│  │  • OpenAPI Documentation                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Service Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │    Auth      │  │    Data      │  │    Query     │  │    Viz     │ │
│  │   Service    │  │   Service    │  │   Engine     │  │  Service   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│         │                 │                  │                │         │
│         │                 └──────────┬───────┘                │         │
│         │                            │                        │         │
│         │                            ▼                        │         │
│         │                   ┌──────────────┐                 │         │
│         │                   │     LLM      │                 │         │
│         │                   │   Service    │                 │         │
│         │                   │  (Claude)    │                 │         │
│         │                   └──────────────┘                 │         │
└─────────┼────────────────────────────┼──────────────────────┼──────────┘
          │                            │                       │
          ▼                            ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Data Layer                                       │
│  ┌──────────────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │    PostgreSQL        │  │    Redis     │  │   File Storage       │ │
│  │  ┌───────────────┐   │  │  (Optional)  │  │   (Local/Cloud)      │ │
│  │  │  Users        │   │  │              │  │                      │ │
│  │  │  Datasets     │   │  │  • Sessions  │  │  • CSV files         │ │
│  │  │  Queries      │   │  │  • Cache     │  │  • Excel files       │ │
│  │  │  Visualizations│  │  │  • Rate      │  │  • Parquet files     │ │
│  │  └───────────────┘   │  │    Limiting  │  │  • JSON files        │ │
│  └──────────────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      External Services                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐   │
│  │  Anthropic API   │  │  Tableau Server  │  │  Web Scraping      │   │
│  │  (Claude AI)     │  │  (Optional)      │  │  (BeautifulSoup)   │   │
│  └──────────────────┘  └──────────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Detailed Component Architecture

### Frontend Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                          │
├─────────────────────────────────────────────────────────────────┤
│  Pages Layer                                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Auth    │ │Dashboard │ │  Upload  │ │  Query   │          │
│  │  Pages   │ │   Page   │ │   Page   │ │  Builder │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│       │             │             │             │               │
├───────┼─────────────┼─────────────┼─────────────┼──────────────┤
│  Components Layer                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Common: Button, Input, Card, Modal, Loading, Table      │  │
│  │ Layout: Header, Sidebar, Footer                          │  │
│  │ Data: FileUploader, DataTable, SchemaViewer             │  │
│  │ Query: QueryEditor, NLInput, QueryHistory               │  │
│  │ Viz: ChartContainer, ChartSelector, VizSuggestions      │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  State Management (Zustand/Redux)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Auth State (user, tokens)                              │  │
│  │ • Dataset State (datasets, current dataset)              │  │
│  │ • Query State (queries, results)                         │  │
│  │ • UI State (loading, modals, notifications)              │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Services/API Layer                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Client (Axios)                                        │  │
│  │ • Request interceptors (add auth token)                  │  │
│  │ • Response interceptors (handle errors, refresh token)   │  │
│  │ • Typed API methods                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
├─────────────────────────────────────────────────────────────────┤
│  API Routes                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /api/auth/*        → Authentication endpoints            │  │
│  │ /api/datasets/*    → Dataset management                  │  │
│  │ /api/query/*       → Query execution                     │  │
│  │ /api/visualize/*   → Visualization generation            │  │
│  │ /health            → Health checks                       │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Middleware Stack                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. CORS Middleware                                       │  │
│  │ 2. JWT Authentication                                    │  │
│  │ 3. Request Validation (Pydantic)                         │  │
│  │ 4. Error Handling                                        │  │
│  │ 5. Logging                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Services                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ AuthService  │  │ DataService  │  │ QueryEngine  │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │• hash_pwd    │  │• parse_file  │  │• exec_sql    │         │
│  │• verify_pwd  │  │• fetch_url   │  │• exec_pandas │         │
│  │• create_jwt  │  │• scrape_web  │  │• nl_to_query │         │
│  │• validate    │  │• infer_schema│  │• validate    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ LLMService   │  │ VizService   │                            │
│  ├──────────────┤  ├──────────────┤                            │
│  │• gen_query   │  │• gen_chart   │                            │
│  │• suggest_viz │  │• suggest     │                            │
│  │• insights    │  │• tableau_exp │                            │
│  └──────────────┘  └──────────────┘                            │
├─────────────────────────────────────────────────────────────────┤
│  Data Access Layer (SQLAlchemy ORM)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Models: User, Dataset, Query, Visualization              │  │
│  │ Async Sessions, Connection Pooling                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. File Upload and Analysis Flow

```
User → Upload File
         │
         ▼
    Frontend validates file type
         │
         ▼
    POST /api/datasets/upload
         │
         ▼
    Backend receives file
         │
         ├─→ Save to file storage
         │
         ├─→ DataService.parse_file()
         │        │
         │        ├─→ Detect file type (CSV/JSON/Excel/Parquet)
         │        ├─→ Parse to DataFrame
         │        └─→ Validate data
         │
         ├─→ DataService.infer_schema()
         │        │
         │        ├─→ Extract column names
         │        ├─→ Detect data types
         │        ├─→ Sample values
         │        └─→ Calculate stats
         │
         └─→ Save metadata to PostgreSQL
                  │
                  ▼
              Return dataset info to user
```

### 2. Natural Language Query Flow

```
User → "Show top 5 customers by revenue"
         │
         ▼
    POST /api/query/natural-language
         │
         ▼
    Load dataset from DB
         │
         ▼
    QueryEngine.natural_language_to_sql()
         │
         ├─→ Build LLM prompt with schema
         │
         ├─→ LLMService.generate_sql_query()
         │        │
         │        ├─→ Call Anthropic API
         │        ├─→ Send schema + question
         │        └─→ Receive SQL query
         │
         ▼
    QueryEngine.execute_sql()
         │
         ├─→ Load DataFrame from file
         │
         ├─→ Execute SQL (pandasql)
         │
         ├─→ Get result DataFrame
         │
         └─→ Create preview (first 100 rows)
                  │
                  ▼
              Save query to DB
                  │
                  ▼
              Return results to user
```

### 3. Visualization Generation Flow

```
User → Request chart suggestions
         │
         ▼
    POST /api/visualize/suggest
         │
         ▼
    Load dataset metadata
         │
         ├─→ Get schema (column types)
         ├─→ Get sample data
         └─→ Get statistics
                  │
                  ▼
    LLMService.suggest_visualizations()
         │
         ├─→ Analyze data types
         │    • Numeric columns
         │    • Categorical columns
         │    • DateTime columns
         │    • Relationships
         │
         ├─→ Call Anthropic API
         │    • Send schema + samples
         │    • Ask for chart recommendations
         │
         └─→ Receive suggestions
                  │
                  ├─→ Bar chart (categorical vs numeric)
                  ├─→ Line chart (time series)
                  ├─→ Scatter plot (numeric vs numeric)
                  └─→ Pie chart (categorical distribution)
                  │
                  ▼
    User selects a chart
         │
         ▼
    POST /api/visualize/generate
         │
         ▼
    VizService.generate_chart()
         │
         ├─→ Load DataFrame
         │
         ├─→ Apply aggregations if needed
         │
         ├─→ Create Plotly chart
         │    OR
         ├─→ Export to Tableau (if configured)
         │
         └─→ Save visualization config
                  │
                  ▼
              Return chart data (Plotly JSON)
```

### 4. Authentication Flow

```
User → Login (email + password)
         │
         ▼
    POST /api/auth/login
         │
         ▼
    AuthService.authenticate_user()
         │
         ├─→ Query DB for user by email
         │
         ├─→ Verify password (bcrypt)
         │
         └─→ If valid:
                  │
                  ├─→ Generate access token (JWT)
                  │    • Expires in 30 minutes
                  │    • Contains user ID
                  │
                  ├─→ Generate refresh token (JWT)
                  │    • Expires in 7 days
                  │
                  └─→ Return both tokens
                           │
                           ▼
    Frontend stores tokens
         │
         ├─→ Access token in memory
         └─→ Refresh token in httpOnly cookie
                  │
                  ▼
    Subsequent requests include:
    Authorization: Bearer <access_token>
         │
         ▼
    Backend validates JWT
         │
         ├─→ Decode token
         ├─→ Check expiration
         ├─→ Extract user ID
         └─→ Load user from DB
                  │
                  ▼
              Request processed with user context
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                               │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ email (VARCHAR, UNIQUE)                                     │
│ hashed_password (VARCHAR)                                   │
│ full_name (VARCHAR, NULL)                                   │
│ is_active (BOOLEAN)                                         │
│ is_superuser (BOOLEAN)                                      │
│ tableau_server_url (VARCHAR, NULL)                          │
│ tableau_credentials (TEXT, NULL, ENCRYPTED)                 │
│ created_at (TIMESTAMP)                                      │
│ updated_at (TIMESTAMP, NULL)                                │
└─────────────────────────────────────────────────────────────┘
                      │
                      │ 1:N
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATASETS                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ user_id (UUID, FK → users.id)                               │
│ name (VARCHAR)                                              │
│ description (TEXT, NULL)                                    │
│ source_type (ENUM: file/url/scrape)                         │
│ source_url (VARCHAR, NULL)                                  │
│ file_path (VARCHAR, NULL)                                   │
│ original_filename (VARCHAR, NULL)                           │
│ file_size (INTEGER, NULL)                                   │
│ file_type (VARCHAR, NULL)                                   │
│ schema (JSONB, NULL)                                        │
│ row_count (INTEGER, NULL)                                   │
│ column_count (INTEGER, NULL)                                │
│ created_at (TIMESTAMP)                                      │
│ updated_at (TIMESTAMP, NULL)                                │
└─────────────────────────────────────────────────────────────┘
                      │
                      │ 1:N
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        QUERIES                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ user_id (UUID, FK → users.id)                               │
│ dataset_id (UUID, FK → datasets.id)                         │
│ name (VARCHAR, NULL)                                        │
│ query_type (ENUM: sql/natural_language/pandas)              │
│ original_input (TEXT)                                       │
│ generated_query (TEXT, NULL)                                │
│ result_preview (JSONB, NULL)                                │
│ result_row_count (VARCHAR, NULL)                            │
│ execution_time_ms (VARCHAR, NULL)                           │
│ error_message (TEXT, NULL)                                  │
│ created_at (TIMESTAMP)                                      │
└─────────────────────────────────────────────────────────────┘
                      │
                      │ 1:N
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    VISUALIZATIONS                           │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ user_id (UUID, FK → users.id)                               │
│ dataset_id (UUID, FK → datasets.id)                         │
│ query_id (UUID, FK → queries.id, NULL)                      │
│ name (VARCHAR, NULL)                                        │
│ description (TEXT, NULL)                                    │
│ chart_type (ENUM: bar/line/scatter/pie/...)                 │
│ config (JSONB)                                              │
│ chart_data (JSONB, NULL)                                    │
│ image_path (VARCHAR, NULL)                                  │
│ tableau_workbook_url (VARCHAR, NULL)                        │
│ created_at (TIMESTAMP)                                      │
│ updated_at (TIMESTAMP, NULL)                                │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Authentication & Authorization

1. **JWT-based Authentication**
   - Access tokens (short-lived, 30 min)
   - Refresh tokens (long-lived, 7 days)
   - Tokens stored securely client-side

2. **Password Security**
   - bcrypt hashing with salt
   - Minimum password requirements
   - Rate limiting on login attempts

3. **Authorization Model**
   - User-scoped resources (datasets, queries, visualizations)
   - Row-level security in database queries
   - Admin role for platform management

### Data Security

1. **File Upload Security**
   - File type validation
   - Size limits (100MB default)
   - Virus scanning (optional integration)
   - Isolated storage per user

2. **SQL Injection Prevention**
   - Parameterized queries
   - Query validation
   - SQL parsing before execution

3. **API Security**
   - CORS configuration
   - Rate limiting
   - Request validation (Pydantic)
   - HTTPS enforcement (production)

## Scalability Considerations

### Horizontal Scaling

```
┌────────────────────────────────────────────────────────┐
│                    Load Balancer                       │
└────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
    ┌───────────┐ ┌───────────┐ ┌───────────┐
    │  FastAPI  │ │  FastAPI  │ │  FastAPI  │
    │ Instance 1│ │ Instance 2│ │ Instance 3│
    └───────────┘ └───────────┘ └───────────┘
            │             │             │
            └─────────────┼─────────────┘
                          ▼
              ┌──────────────────────┐
              │   PostgreSQL         │
              │   (Primary/Replica)  │
              └──────────────────────┘
```

### Caching Strategy

- Redis for session storage
- Query result caching (configurable TTL)
- LLM response caching for identical queries
- Static file caching (CDN)

### Performance Optimizations

1. **Database**
   - Connection pooling
   - Query optimization
   - Indexes on frequently queried columns
   - Async operations

2. **File Processing**
   - Chunked file upload
   - Background processing for large files
   - DataFrame sampling for preview

3. **LLM Calls**
   - Response caching
   - Batch processing
   - Streaming responses

## Technology Stack Details

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend Framework | React | 18+ | UI rendering |
| Build Tool | Vite | 5+ | Fast dev & build |
| Type Safety | TypeScript | 5+ | Type checking |
| Styling | TailwindCSS | 3+ | Utility-first CSS |
| Backend Framework | FastAPI | 0.115+ | REST API |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Database | PostgreSQL | 14+ | Primary data store |
| Cache | Redis | 7+ | Session & caching |
| Data Processing | Pandas | 2.2+ | DataFrame operations |
| SQL Engine | pandasql | 0.7+ | SQL on DataFrames |
| Visualization | Plotly | 5.24+ | Interactive charts |
| LLM | Claude (Anthropic) | Sonnet 4.5 | NL query & suggestions |
| Auth | JWT (python-jose) | 3.3+ | Token auth |
| Password Hash | bcrypt (passlib) | 1.7+ | Password security |

## Deployment Architecture

### Development Environment
```
localhost:5173 (Frontend - Vite dev server)
localhost:8000 (Backend - uvicorn)
localhost:5432 (PostgreSQL)
localhost:6379 (Redis)
```

### Production Environment
```
┌─────────────────────────────────────────┐
│              CDN (Static Assets)        │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Frontend (Vercel/Netlify)       │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│     Backend (AWS/GCP/Azure Container)   │
│     • FastAPI in Docker                 │
│     • Gunicorn + Uvicorn workers        │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────────────┐   ┌──────────────────┐
│  PostgreSQL   │   │  Object Storage  │
│  (Managed)    │   │  (S3/GCS/Azure)  │
└───────────────┘   └──────────────────┘
```

## Monitoring & Observability

1. **Logging**
   - Structured logging (JSON)
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Request/response logging

2. **Metrics**
   - API response times
   - Database query performance
   - LLM call latency
   - Error rates

3. **Health Checks**
   - `/health` - Basic liveness
   - `/health/db` - Database connectivity
   - Periodic background checks

## Future Enhancements

1. **Collaborative Features**
   - Shared datasets
   - Query templates
   - Comments and annotations

2. **Advanced Analytics**
   - Machine learning model training
   - Predictive analytics
   - Anomaly detection

3. **Integration Ecosystem**
   - Google Sheets connector
   - Snowflake/BigQuery integration
   - BI tool exports (Power BI, Looker)

4. **Enterprise Features**
   - SSO/SAML authentication
   - Role-based access control
   - Audit logging
   - Data governance
