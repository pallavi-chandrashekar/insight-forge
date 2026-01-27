# Feature: Query Execution System

## Overview
Enable users to query their datasets using multiple paradigms: SQL, Pandas-style operations, and natural language queries.

## Status
🚧 **TO BE IMPLEMENTED**

---

## User Stories

### US-1: SQL Query Execution
**As a** data analyst
**I want to** write SQL queries against my datasets
**So that** I can extract and transform data using familiar SQL syntax

**Acceptance Criteria:**
- [ ] Support SELECT statements
- [ ] Support WHERE clauses with conditions
- [ ] Support JOIN operations (multiple datasets)
- [ ] Support GROUP BY and aggregations
- [ ] Support ORDER BY and LIMIT
- [ ] Support subqueries
- [ ] Syntax highlighting in editor
- [ ] Auto-completion for column names
- [ ] Query validation before execution
- [ ] Display results in table format
- [ ] Save queries for reuse
- [ ] Query execution time tracking

### US-2: Pandas-Style Operations
**As a** Python developer
**I want to** use Pandas-style operations
**So that** I can leverage my Python knowledge for data manipulation

**Acceptance Criteria:**
- [ ] Filter operations (df.query())
- [ ] Column selection (df[cols])
- [ ] Sorting (df.sort_values())
- [ ] Grouping and aggregation (df.groupby())
- [ ] Join operations (df.merge())
- [ ] Drop duplicates
- [ ] Handle missing values
- [ ] Visual operation builder (no code)
- [ ] Chain multiple operations
- [ ] Preview intermediate results

### US-3: Natural Language Queries
**As a** business user
**I want to** ask questions in plain English
**So that** I can analyze data without knowing SQL or Python

**Acceptance Criteria:**
- [ ] Natural language input field
- [ ] AI-powered query translation (Claude)
- [ ] Show generated SQL/Pandas code
- [ ] Execute translated query
- [ ] Handle ambiguous questions
- [ ] Suggest clarifying questions
- [ ] Learn from query history
- [ ] Example queries/templates

### US-4: Query History
**As a** user
**I want to** see my past queries
**So that** I can reuse or modify them

**Acceptance Criteria:**
- [ ] List all past queries
- [ ] Show query text, type, dataset, timestamp
- [ ] Filter by dataset
- [ ] Search queries by text
- [ ] Re-execute previous queries
- [ ] Edit and save queries
- [ ] Delete query history

### US-5: Query Results Management
**As a** user
**I want to** work with query results
**So that** I can visualize or export the data

**Acceptance Criteria:**
- [ ] Display results in table
- [ ] Pagination for large results
- [ ] Column sorting
- [ ] Column filtering
- [ ] Export to CSV/JSON/Excel
- [ ] Create visualization from results
- [ ] Save results as new dataset
- [ ] Share query results (future)

---

## API Endpoints

### 1. Execute SQL Query
```http
POST /api/query/execute
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "dataset_id": "uuid",
  "query_type": "sql",
  "query": "SELECT * FROM df WHERE value > 100 LIMIT 10",
  "save": true,
  "name": "High Value Records"
}

Response: 200 OK
{
  "id": "query-uuid",
  "query_type": "sql",
  "generated_query": "SELECT * FROM df WHERE value > 100 LIMIT 10",
  "result_preview": {
    "columns": ["id", "name", "value"],
    "data": [[1, "Alice", 150], ...],
    "row_count": 10,
    "total_rows": 45
  },
  "execution_time_ms": 125,
  "created_at": "2024-01-25T10:00:00Z"
}
```

### 2. Execute Pandas Operations
```http
POST /api/query/execute
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "dataset_id": "uuid",
  "query_type": "pandas",
  "operations": [
    {"type": "filter", "condition": "value > 100"},
    {"type": "sort", "by": "value", "ascending": false},
    {"type": "head", "n": 10}
  ],
  "save": true,
  "name": "Top 10 High Values"
}

Response: 200 OK
{
  "id": "query-uuid",
  "query_type": "pandas",
  "operations": [...],
  "result_preview": {...},
  "execution_time_ms": 89
}
```

### 3. Natural Language Query
```http
POST /api/query/natural-language
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "dataset_id": "uuid",
  "question": "What are the top 5 products by revenue?",
  "save": true
}

Response: 200 OK
{
  "id": "query-uuid",
  "query_type": "natural_language",
  "original_input": "What are the top 5 products by revenue?",
  "generated_query": "SELECT product, SUM(revenue) as total FROM df GROUP BY product ORDER BY total DESC LIMIT 5",
  "explanation": "This query groups products and sums their revenue, then sorts by total revenue descending",
  "result_preview": {...},
  "execution_time_ms": 1250,
  "llm_time_ms": 890
}
```

### 4. Get Query History
```http
GET /api/query/history?dataset_id=uuid&skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "High Value Records",
    "query_type": "sql",
    "original_input": "SELECT...",
    "result_row_count": 45,
    "created_at": "2024-01-25T10:00:00Z"
  },
  ...
]
```

### 5. Re-execute Query
```http
POST /api/query/{id}/execute
Authorization: Bearer <token>

Response: 200 OK
{
  "result_preview": {...},
  "execution_time_ms": 120
}
```

### 6. Delete Query
```http
DELETE /api/query/{id}
Authorization: Bearer <token>

Response: 204 No Content
```

---

## Technical Implementation

### Backend Components

#### QueryEngine (`backend/app/services/query_engine.py`)

**Methods:**

```python
class QueryEngine:
    async def execute_sql(
        self,
        df: pd.DataFrame,
        sql: str
    ) -> pd.DataFrame:
        """Execute SQL query using pandasql"""
        # Validate SQL (no DDL/DML, only SELECT)
        # Use pandasql.sqldf() to execute
        # Handle errors gracefully
        # Return result DataFrame

    async def execute_pandas_operations(
        self,
        df: pd.DataFrame,
        operations: List[dict]
    ) -> pd.DataFrame:
        """Execute chain of Pandas operations"""
        # Iterate through operations
        # Apply each operation to df
        # Supported operations:
        #   - filter: df.query(condition)
        #   - select: df[columns]
        #   - sort: df.sort_values(by, ascending)
        #   - groupby: df.groupby(by).agg(agg)
        #   - head/tail: df.head(n)
        #   - drop_na: df.dropna(subset=columns)
        #   - rename: df.rename(columns=mapping)
        # Return final DataFrame

    async def natural_language_to_sql(
        self,
        question: str,
        schema: dict
    ) -> QueryResult:
        """Convert natural language to SQL using LLM"""
        # Call LLMService.generate_sql_query()
        # Validate generated SQL
        # Return SQL and explanation

    async def validate_sql(self, sql: str) -> ValidationResult:
        """Validate SQL query for safety"""
        # Check for forbidden keywords (DROP, DELETE, UPDATE, etc.)
        # Parse SQL to verify syntax
        # Check for injection patterns
        # Return validation result

    async def optimize_query(self, sql: str) -> str:
        """Optimize SQL query (future enhancement)"""
        # Analyze query plan
        # Suggest optimizations
        # Return optimized SQL
```

#### Query Routes (`backend/app/api/routes/query.py`)

**Endpoints:**
- `POST /execute` - Execute SQL or Pandas query
- `POST /natural-language` - Natural language query
- `GET /history` - Get query history
- `POST /{id}/execute` - Re-execute saved query
- `DELETE /{id}` - Delete query

**Dependencies:**
- Current user (JWT)
- QueryEngine service
- DataService (load datasets)
- LLMService (NL queries)
- Database session

**Error Handling:**
- 400 Bad Request: Invalid SQL, invalid operations
- 403 Forbidden: Unsafe query detected
- 404 Not Found: Dataset/query not found
- 500 Internal Server Error: Execution failures

#### LLM Integration

**Prompt Template for SQL Generation:**
```
You are a SQL expert. Generate a SQL query based on the user's question.

The data is stored in a table called 'df'.

Schema:
- id (int64): sample values = [1, 2, 3]
- name (string): sample values = ["Alice", "Bob", "Charlie"]
- value (float64): sample values = [100.5, 200.0, 150.3]
- date (datetime): sample values = ["2024-01-01", "2024-01-02", ...]

IMPORTANT RULES:
1. Only return the SQL query, nothing else
2. Use standard SQL syntax compatible with SQLite
3. Use column names exactly as they appear
4. Handle potential NULL values
5. Do not use DDL statements (CREATE, DROP, ALTER)
6. Only use SELECT statements

Question: {user_question}

Generate the SQL query:
```

### Frontend Components

#### Query Builder Page (`frontend/src/pages/Query.tsx`)

**State:**
- Selected dataset
- Query mode (sql, pandas, natural_language)
- Query input
- Results data
- Loading state
- Error messages

**Components:**
- Dataset selector dropdown
- Query mode tabs
- SQL Editor (Monaco/CodeMirror)
  - Syntax highlighting
  - Auto-completion
  - Line numbers
- Pandas Operations Builder
  - Visual operation picker
  - Operation configuration
  - Preview chain
- Natural Language Input
  - Text area
  - Example questions
  - Suggestions
- Execute button
- Results table
  - Pagination
  - Sorting
  - Filtering
- Export options
- Save query dialog

#### Query History Component

**Props:**
- Dataset ID (optional filter)

**State:**
- Query list
- Selected query
- Search term

**Features:**
- List past queries
- Search/filter
- Click to re-execute
- Edit and save
- Delete queries

### Database Schema

```sql
CREATE TABLE queries (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    name VARCHAR(255),
    query_type VARCHAR(50) NOT NULL, -- 'sql', 'natural_language', 'pandas'
    original_input TEXT NOT NULL,
    generated_query TEXT,
    operations JSONB, -- For pandas operations
    result_preview JSONB,
    result_row_count INTEGER,
    execution_time_ms INTEGER,
    llm_time_ms INTEGER, -- Time spent in LLM call
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_queries_user_id ON queries(user_id);
CREATE INDEX idx_queries_dataset_id ON queries(dataset_id);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
```

---

## Query Execution Flow

```
User enters query → Frontend validates input
         │
         ▼
    POST /api/query/execute
         │
         ├─→ Load dataset from storage
         │
         ├─→ If SQL:
         │    ├─→ Validate SQL syntax
         │    ├─→ Check for unsafe operations
         │    └─→ Execute with pandasql
         │
         ├─→ If Pandas:
         │    ├─→ Validate operations
         │    └─→ Apply operations sequentially
         │
         ├─→ If Natural Language:
         │    ├─→ Call LLM to generate SQL
         │    ├─→ Validate generated SQL
         │    └─→ Execute generated SQL
         │
         ├─→ Get result DataFrame
         │
         ├─→ Create preview (limit rows)
         │
         ├─→ Save query to database
         │
         └─→ Return results to user
```

---

## Security Considerations

1. **SQL Injection Prevention**
   - No DDL/DML statements allowed
   - No UNION, EXEC, or dangerous keywords
   - Parameterized queries where possible
   - SQL parsing and validation

2. **Query Validation**
   - Whitelist of allowed SQL keywords
   - Operation validation for Pandas
   - Timeout limits (30 seconds)
   - Memory limits

3. **Data Access Control**
   - Users can only query their own datasets
   - Row-level security enforced
   - Query history is user-scoped

---

## Performance Optimizations

1. **Query Execution**
   - In-memory DataFrame operations
   - Lazy evaluation where possible
   - Result caching for identical queries
   - Pagination for large results

2. **LLM Calls**
   - Cache responses for identical questions
   - Batch similar requests (future)
   - Streaming responses (future)
   - Timeout limits

3. **Result Handling**
   - Sample large results for preview
   - Async execution for slow queries
   - Background job processing (future)

**Benchmarks (Target):**
- Simple SELECT: < 100ms
- Aggregations: < 500ms
- Natural language: < 2 seconds
- Complex joins: < 1 second

---

## Testing Strategy

### Unit Tests
- [ ] SQL validation
- [ ] SQL execution
- [ ] Pandas operations
- [ ] Query result formatting
- [ ] Error handling

### Integration Tests
- [ ] End-to-end query flow
- [ ] Natural language translation
- [ ] Query history management
- [ ] Multi-dataset queries

### Manual Testing
- [ ] Execute various SQL queries
- [ ] Test Pandas operations
- [ ] Try natural language queries
- [ ] Verify query history
- [ ] Test error scenarios

---

## Dependencies

**Backend:**
- pandasql >= 0.7.3 (SQL on DataFrames)
- sqlparse >= 0.4.4 (SQL parsing & validation)
- anthropic >= 0.39.0 (LLM integration)

**Frontend:**
- @monaco-editor/react >= 4.6.0 (SQL editor)
- react-syntax-highlighter >= 15.5.0 (Code display)

---

## Future Enhancements

1. **Query Optimization**
   - Suggest query improvements
   - Index recommendations
   - Performance profiling

2. **Advanced SQL Features**
   - Window functions
   - Common Table Expressions (CTEs)
   - Recursive queries

3. **Collaboration**
   - Share queries with team
   - Query templates
   - Parameterized queries

4. **Scheduled Queries**
   - Run queries on schedule
   - Email results
   - Trigger alerts

5. **Visual Query Builder**
   - Drag-and-drop interface
   - No-code query creation
   - Visual joins and filters

---

## Success Metrics

- Query execution success rate > 95%
- Average query execution time < 1 second
- Natural language accuracy > 80%
- User satisfaction rating > 4.5/5
- Queries per user per week

---

## Documentation

- [ ] API documentation (Swagger)
- [ ] User guide with examples
- [ ] SQL reference guide
- [ ] Pandas operations guide
- [ ] Natural language query tips
- [ ] This feature spec
