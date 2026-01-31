# InsightForge Features Index

## Overview

This document provides a comprehensive overview of all InsightForge features, their status, dependencies, and integration points.

---

## Feature Roadmap

#### 1. Data Upload & Dataset Management
**Status:** ✅ DOCUMENTED (Ready for Implementation)

**File:** `01-data-upload-management.md`

**Description:** Import data from multiple sources (CSV, JSON, Excel, Parquet files, URLs, web scraping) and manage datasets.

**Key Capabilities:**
- File upload with drag-and-drop
- URL data import
- Web table scraping
- Automatic schema inference
- Dataset preview and management
- Multi-format support

**API Endpoints:**
- `POST /api/datasets/upload` - Upload file
- `POST /api/datasets/from-url` - Import from URL
- `POST /api/datasets/scrape` - Scrape web table
- `GET /api/datasets` - List datasets
- `GET /api/datasets/{id}` - Get dataset details
- `GET /api/datasets/{id}/preview` - Preview data
- `DELETE /api/datasets/{id}` - Delete dataset

**Dependencies:** None (Foundation feature)

---

#### 2. Context File Management
**Status:** ✅ DOCUMENTED (Ready for Implementation)

**File:** `context-file-management.md`

**Description:** Define relationships, custom metrics, business rules, and filters across multiple datasets using Markdown files with YAML frontmatter.

**Key Capabilities:**
- Context definition (YAML frontmatter)
- Multi-level validation (schema, semantic, circular dependency)
- Relationship management (inner, left, right, outer joins)
- Custom metrics (calculated fields)
- Business rules (validation, quality, constraints)
- Pre-defined filters
- Version control

**API Endpoints:**
- `POST /api/contexts` - Create context
- `GET /api/contexts/{id}` - Get context
- `GET /api/contexts` - List contexts
- `PUT /api/contexts/{id}` - Update context
- `DELETE /api/contexts/{id}` - Delete context
- `POST /api/contexts/validate` - Validate context
- `GET /api/contexts/{id}/relationships` - Get relationships
- `GET /api/contexts/{id}/metrics` - Get metrics
- `GET /api/contexts/{id}/export` - Export context

**Dependencies:**
- Feature 01: Data Upload (for dataset references)

**Example Context:**
```yaml
---
name: ecommerce_basic
version: 1.0.0
description: Basic e-commerce context

datasets:
  - id: customers_ds
    dataset_id: uuid
  - id: orders_ds
    dataset_id: uuid

relationships:
  - id: customer_orders
    left_dataset: customers_ds
    right_dataset: orders_ds
    join_type: left
    conditions:
      - left_column: customer_id
        operator: "="
        right_column: customer_id

metrics:
  - id: total_revenue
    expression: SUM(o.order_amount)
    data_type: float
---
```

---

#### 3. Query Engine (Single & Multi-Dataset)
**Status:** 🚧 IN PROGRESS (Unified, ready for implementation)

**File:** `02-query-engine.md`

**Description:** Comprehensive query engine supporting both single-dataset and multi-dataset queries with SQL, Pandas operations, and natural language.

**Key Capabilities:**

**Single-Dataset:**
- SQL query execution (pandasql)
- Pandas-style operations
- Natural language to SQL translation (Claude AI)
- Query validation and history

**Multi-Dataset (Context-Aware):**
- Natural language queries across datasets
- Automatic JOIN generation from context relationships
- Custom metric expansion
- Business rule enforcement
- Query templates and reusability
- Performance caching and optimization

**Query Types:**
1. **SQL**: Direct SQL on single or multiple datasets
2. **Pandas**: Pandas-style operations
3. **Natural Language**: Plain English queries
4. **Structured**: Declarative multi-dataset query
5. **Metric-Based**: Aggregation queries using context metrics

**API Endpoints:**

*Single-Dataset:*
- `POST /api/query/execute` - Execute SQL or Pandas query
- `POST /api/query/natural-language` - Natural language query

*Multi-Dataset:*
- `POST /api/queries/execute` - Execute multi-dataset query
- `POST /api/queries/structured` - Execute structured query
- `POST /api/queries/save` - Save query as template
- `POST /api/queries/templates/{id}/execute` - Execute template
- `POST /api/queries/explain` - Get query explanation

*Common:*
- `GET /api/query/history` - Get query history
- `DELETE /api/query/{id}` - Delete query

**Dependencies:**
- Feature 01: Data Upload (for datasets)
- Feature 02: Context File Management (for multi-dataset queries)
- LLM Service (for natural language)

---

#### 4. Visualization & Chart Generation
**Status:** 🚧 IN PROGRESS (Needs implementation)

**File:** `03-visualization-charts.md`

**Description:** Create interactive visualizations with AI-powered chart suggestions.

**Key Capabilities:**
- AI-powered chart suggestions (Claude AI)
- Manual chart creation
- Interactive Plotly charts
- Multiple chart types (bar, line, scatter, pie, histogram, heatmap, box, area)
- Visualization from query results
- Tableau integration (optional)

**API Endpoints:**
- `POST /api/visualize/suggest` - Get AI chart suggestions
- `POST /api/visualize/generate` - Generate chart
- `GET /api/visualize` - List visualizations
- `GET /api/visualize/{id}` - Get visualization
- `PUT /api/visualize/{id}` - Update visualization
- `DELETE /api/visualize/{id}` - Delete visualization
- `POST /api/visualize/{id}/tableau-export` - Export to Tableau

**Dependencies:**
- Feature 01: Data Upload (for datasets)
- Feature 03: Query Engine (for query results)
- LLM Service (for suggestions)

**Integration:**
```
User Question → Context Definition → Multi-Dataset Query Engine
                    ↓
            Relationships, Metrics, Rules
                    ↓
            Optimized SQL Generation
                    ↓
            Execute across datasets
                    ↓
            Formatted Results
```

---

### 📋 Planned Features

#### 5. Authentication & User Management
**Status:** ✅ IMPLEMENTED

**Description:** JWT-based authentication, user registration, login, and profile management.

**Implementation:**
- JWT access tokens (30 min expiry)
- Refresh tokens (7 days expiry)
- bcrypt password hashing
- User-scoped data isolation

**API Endpoints:**
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`

---

#### 6. Dashboard & Analytics
**Status:** 📋 PLANNED

**Description:** User dashboard showing recent activity, datasets, queries, and visualizations.

**Key Capabilities:**
- Dataset overview cards
- Recent queries list
- Saved visualizations gallery
- Activity timeline
- Usage statistics

---

#### 7. Collaboration Features
**Status:** 📋 PLANNED

**Description:** Share datasets, queries, and visualizations with team members.

**Key Capabilities:**
- Dataset sharing
- Query templates sharing
- Visualization embedding
- Comments and annotations
- Team workspaces

---

#### 8. Advanced Analytics
**Status:** 📋 PLANNED

**Description:** Machine learning models, predictive analytics, anomaly detection.

**Key Capabilities:**
- Auto-ML for predictions
- Anomaly detection
- Trend analysis
- Forecasting

---

#### 9. Performance & Caching
**Status:** 📋 PLANNED

**Description:** Redis caching, query result caching, performance optimization.

**Key Capabilities:**
- Query result caching
- Context caching
- LLM response caching
- Background job processing

---

#### 12. Testing & Quality Assurance
**Status:** 📋 PLANNED

**Description:** Comprehensive testing suite for backend and frontend.

**Test Types:**
- Unit tests (pytest, Jest)
- Integration tests
- E2E tests (Playwright/Cypress)
- Performance tests

---

## Feature Dependencies Graph

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Feature Dependencies                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  01. Data Upload     │  (Foundation)
│  ✅ IMPLEMENTED      │
└──────────┬───────────┘
           │
           ├──────────────────────┬──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ 02. Context Files    │  │ 03. Query Engine     │  │ 04. Visualization    │
│ ✅ DOCUMENTED        │  │    (Unified)         │  │ 🚧 IN PROGRESS       │
│                      │  │ 🚧 IN PROGRESS       │  │                      │
│ • Relationships      │  │                      │  │ • AI Suggestions     │
│ • Metrics            │  │ • Single Dataset     │  │ • Plotly Charts      │
│ • Business Rules     │  │ • Multi-Dataset      │  │ • Tableau Export     │
│ • Filters            │  │ • Context-Aware      │  │                      │
└──────────┬───────────┘  └──────────────────────┘  └──────────────────────┘
           │                         ▲
           └─────────────────────────┘
                 (Context integration)
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                             │
├─────────────────────────────────────────────────────────────────────┤
│  Upload Page  │  Dashboard  │  Query Builder  │  Visualize Page    │
│  Context Mgmt │             │  Context Select │  AI Suggestions    │
└───────────────┴─────────────┴─────────────────┴────────────────────┘
                              │
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────┤
│ DataService │ ContextService │ QueryEngine │ VizService │ LLMService│
│             │                │             │            │           │
│ • Upload    │ • Parse YAML   │ • SQL Exec  │ • Plotly   │ • Claude  │
│ • Scrape    │ • Validate     │ • Pandas    │ • Suggest  │ • NL→SQL  │
│ • Schema    │ • Relationships│ • NL Query  │ • Tableau  │ • Explain │
│             │ • Metrics      │ • Multi-DS  │            │           │
└─────────────┴────────────────┴─────────────┴────────────┴───────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Data Layer (PostgreSQL + Redis)                   │
├─────────────────────────────────────────────────────────────────────┤
│  Users  │  Datasets  │  Contexts  │  Queries  │  Visualizations    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1: Core Features (Weeks 1-4)
- [x] Feature 01: Data Upload & Management ✅
- [x] Feature 07: Authentication ✅
- [ ] Feature 03: Query Execution (single dataset)
- [ ] Feature 04: Visualization (basic charts)

### Phase 2: Context & Multi-Dataset (Weeks 5-8)
- [ ] Feature 02: Context File Management
- [ ] Feature 05: Multi-Dataset Query Engine
- [ ] Feature 06: Context-Aware Queries
- [ ] Advanced Visualization (AI suggestions)

### Phase 3: Polish & Performance (Weeks 9-12)
- [ ] Feature 08: Dashboard & Analytics
- [ ] Feature 11: Performance & Caching
- [ ] Feature 12: Testing & QA
- [ ] Documentation & User Guides

### Phase 4: Advanced Features (Weeks 13-16)
- [ ] Feature 09: Collaboration
- [ ] Feature 10: Advanced Analytics
- [ ] Enterprise features

---

## Development Workflow

### For Each Feature:

1. **Design Phase**
   - Review feature spec document
   - Identify dependencies
   - Design API contracts
   - Create database migrations if needed

2. **Backend Implementation**
   - Implement models (SQLAlchemy)
   - Implement services (business logic)
   - Implement API routes (FastAPI)
   - Write unit tests

3. **Frontend Implementation**
   - Create page components
   - Implement API client methods
   - Add state management
   - Create UI components

4. **Integration Testing**
   - End-to-end tests
   - API integration tests
   - Performance tests

5. **Documentation**
   - Update API documentation (Swagger)
   - Write user guides
   - Create usage examples

---

## Parallel Development Tracks

### Track A: Core Query Features
**Team:** Backend + AI Integration
- Feature 03: Query Execution
- Feature 05: Multi-Dataset Query Engine
- Feature 06: Context-Aware Queries
- LLM Service enhancements

### Track B: Visualization & UI
**Team:** Frontend + Data Viz
- Feature 04: Visualization & Charts
- Feature 08: Dashboard
- UI/UX improvements
- Component library

### Track C: Context Management
**Team:** Backend + Data Modeling
- Feature 02: Context File Management
- Validation engine
- Relationship resolver
- Schema validation

### Track D: Infrastructure
**Team:** DevOps + Performance
- Feature 11: Caching & Performance
- Feature 12: Testing
- CI/CD pipeline
- Monitoring & logging

---

## Success Metrics

### Feature 01: Data Upload
- ✅ Upload success rate: 98% (Target: > 95%)
- ✅ Average upload time: 2-3s for 10MB files (Target: < 5s)
- ✅ Multi-format support: CSV, JSON, Excel, Parquet
- ✅ Manual testing completed

### Feature 02: Context Management
- Target: Context validation success rate > 95%
- Target: Context load time < 500ms
- Target: User adoption rate > 40%

### Feature 03: Query Execution
- Target: Query execution time < 2s (simple queries)
- Target: NL query accuracy > 80%
- Target: Query success rate > 95%

### Feature 04: Visualization
- Target: Chart generation time < 1s
- Target: AI suggestion accuracy > 85%
- Target: User satisfaction > 4.5/5

### Feature 05: Multi-Dataset Queries
- Target: Multi-dataset query time < 3s
- Target: Join optimization effectiveness > 70%
- Target: Complex query success rate > 90%

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** |
| Framework | React | 18+ |
| Build Tool | Vite | 5+ |
| Language | TypeScript | 5+ |
| Styling | TailwindCSS | 3+ |
| State | Zustand | 4+ |
| HTTP Client | Axios | 1.6+ |
| Charts | Plotly.js | 2.27+ |
| **Backend** |
| Framework | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 14+ |
| Cache | Redis | 7+ (optional) |
| Data Processing | Pandas | 2.2+ |
| SQL Engine | pandasql | 0.7+ |
| Viz Library | Plotly | 5.24+ |
| LLM | Anthropic Claude | Sonnet 4.5 |
| Auth | JWT (python-jose) | 3.3+ |
| Password | bcrypt (passlib) | 1.7+ |
| **Infrastructure** |
| Containerization | Docker | 24+ |
| Orchestration | Docker Compose | 2+ |
| Web Server | Uvicorn | 0.32+ |

---

## Quick Links

### Documentation
- [Architecture Overview](../ARCHITECTURE.md)
- [README](../../README.md)
- [Docker Setup](../../README.docker.md)
- [API Documentation](http://localhost:8000/docs) (when running)

### Feature Specs
1. [Data Upload & Management](01-data-upload-management.md) ✅
2. [Context File Management](context-file-management.md) ✅
3. [Query Execution](02-query-execution.md) 🚧
4. [Visualization & Charts](03-visualization-charts.md) 🚧
5. [Multi-Dataset Query Engine](multi-dataset-query-engine.md) 🚧
6. [Context-Aware Queries](04-context-aware-queries.md) 🚧

### Code Locations
- **Backend**: `/backend/app/`
  - Models: `/backend/app/models/`
  - Services: `/backend/app/services/`
  - Routes: `/backend/app/api/routes/`
  - Config: `/backend/app/core/`

- **Frontend**: `/frontend/src/`
  - Pages: `/frontend/src/pages/`
  - Components: `/frontend/src/components/`
  - Services: `/frontend/src/services/`
  - Store: `/frontend/src/store/`

---

## Getting Started for Developers

### 1. Setup Development Environment
```bash
# Clone repository
git clone <repo-url>
cd insight-forge

# Start Docker services
docker-compose up -d

# Verify services
docker-compose ps

# Access application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 2. Choose a Feature to Implement
- Review feature spec in `docs/features/`
- Check dependencies are implemented
- Identify integration points

### 3. Create Feature Branch
```bash
git checkout -b feature/query-execution
```

### 4. Implement Feature
- Backend: Models → Services → Routes → Tests
- Frontend: Components → Pages → Integration
- Test locally with Docker hot-reload

### 5. Submit for Review
```bash
git add .
git commit -m "Implement query execution feature"
git push origin feature/query-execution
# Create PR
```

---

## Contact & Support

For questions about features or implementation:
- Create an issue on GitHub
- Check existing feature specs
- Review architecture documentation
- Consult API documentation

---

**Last Updated:** 2026-01-26
**Version:** 1.0.0
