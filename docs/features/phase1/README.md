# Phase 1: Core Features (Weeks 1-4)

## Overview
Foundation features enabling basic data analysis capabilities with single-dataset queries and visualizations.

## Status
📋 **READY TO START** - Infrastructure complete, features ready for implementation

---

## Features

### 📋 1. Data Upload & Dataset Management
**File:** `01-data-upload-management.md`
**Status:** 📋 PLANNED (Fully specified, ready to implement)

Import data from multiple sources and manage datasets.

**Capabilities:**
- File upload (CSV, JSON, Excel, Parquet)
- URL data import
- Web table scraping
- Automatic schema inference
- Dataset preview and management

**Infrastructure:**
- Backend models scaffolded
- API routes defined
- Frontend pages structured

---

### 📋 2. Authentication & User Management
**Status:** 📋 PLANNED

JWT-based authentication with user registration and login.

**To Implement:**
- Backend: `backend/app/api/routes/auth.py`
- JWT access tokens (30 min)
- Refresh tokens (7 days)
- bcrypt password hashing
- Frontend auth pages

---

### 📋 3. Query Engine (Single & Multi-Dataset)
**File:** `02-query-engine.md`
**Status:** 📋 PLANNED

**Phase 1 Focus:** Single-dataset queries
- SQL query execution (pandasql)
- Pandas-style operations
- Natural language to SQL (Claude AI)
- Query validation and history

**Phase 2 Extension:** Multi-dataset capabilities (see Phase 2)

---

### 📋 4. Visualization & Charts
**File:** `03-visualization-charts.md`
**Status:** 📋 PLANNED

**Phase 1 Focus:** Basic visualizations
- Manual chart creation
- Plotly chart rendering
- Chart types: bar, line, scatter, pie, histogram
- Save visualizations

**Phase 2 Extension:** AI-powered suggestions (see Phase 2)

---

## Implementation Order

1. 📋 **Authentication** - Week 1
   - User registration and login
   - JWT token management
   - Frontend auth pages

2. 📋 **Data Upload** - Week 1-2
   - File upload implementation
   - URL import
   - Web scraping
   - Dataset management UI

3. 📋 **Query Engine (Single-Dataset)** - Week 2-3
   - SQL & Pandas execution
   - Natural language integration
   - Query history

4. 📋 **Visualization (Basic)** - Week 3-4
   - Chart generation
   - Save & display visualizations
   - Chart configuration UI

---

## Dependencies

```
Docker Setup (✅) ──┐
                    │
Infrastructure (✅) ─┼──→ Authentication (📋) ──┐
                    │                           │
                    └──→ Data Upload (📋) ──────┼──→ Query Engine (📋) ──→ Visualization (📋)
                                                │
                                                └──→ Frontend Pages (📋)
```

---

## Success Criteria

- [ ] Users can upload and manage datasets
- [ ] Users can register and login
- [ ] Users can execute SQL queries on datasets
- [ ] Users can use natural language queries
- [ ] Users can create basic visualizations
- [ ] All Phase 1 features have >90% test coverage
- [ ] API response times <500ms for typical operations

---

## Next Phase

See [Phase 2](../phase2/README.md) for context management and multi-dataset queries.
