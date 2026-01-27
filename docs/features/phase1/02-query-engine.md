# Feature: Query Engine (Single & Multi-Dataset)

## Overview
Comprehensive query engine enabling users to execute queries on single datasets or across multiple datasets using SQL, Pandas-style operations, and natural language. Supports context-aware multi-dataset queries with automatic relationship resolution, custom metrics, and business rules.

## Status
🚧 **TO BE IMPLEMENTED**

---

## Table of Contents
1. [Single-Dataset Queries](#single-dataset-queries)
2. [Multi-Dataset Queries with Context](#multi-dataset-queries-with-context)
3. [API Endpoints](#api-endpoints)
4. [Architecture](#architecture)
5. [Implementation](#implementation)
6. [Testing](#testing)

---

## Single-Dataset Queries

### Overview
Query a single dataset using SQL, Pandas operations, or natural language without requiring context definitions.

### User Stories

#### US-1: SQL Query Execution
**As a** data analyst
**I want to** write SQL queries against my datasets
**So that** I can extract and transform data using familiar SQL syntax

**Acceptance Criteria:**
- [ ] Support SELECT statements
- [ ] Support WHERE clauses with conditions
- [ ] Support GROUP BY and aggregations
- [ ] Support ORDER BY and LIMIT
- [ ] Syntax highlighting in editor
- [ ] Auto-completion for column names
- [ ] Query validation before execution
- [ ] Display results in table format
- [ ] Save queries for reuse
- [ ] Query execution time tracking

#### US-2: Pandas-Style Operations
**As a** Python developer
**I want to** use Pandas-style operations
**So that** I can leverage my Python knowledge for data manipulation

**Acceptance Criteria:**
- [ ] Filter operations (df.query())
- [ ] Column selection (df[cols])
- [ ] Sorting (df.sort_values())
- [ ] Grouping and aggregation (df.groupby())
- [ ] Drop duplicates
- [ ] Handle missing values
- [ ] Visual operation builder (no code)
- [ ] Chain multiple operations
- [ ] Preview intermediate results

#### US-3: Natural Language Queries (Single Dataset)
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
- [ ] Example queries/templates

### API Endpoints (Single Dataset)

#### 1. Execute SQL Query
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

#### 2. Execute Pandas Operations
```http
POST /api/query/execute
Authorization: Bearer <token>

Request:
{
  "dataset_id": "uuid",
  "query_type": "pandas",
  "operations": [
    {"type": "filter", "condition": "value > 100"},
    {"type": "sort", "by": "value", "ascending": false},
    {"type": "head", "n": 10}
  ],
  "save": true
}
```

#### 3. Natural Language Query (Single Dataset)
```http
POST /api/query/natural-language
Authorization: Bearer <token>

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
  "explanation": "This query groups products and sums their revenue",
  "result_preview": {...},
  "execution_time_ms": 1250
}
```

---

## Multi-Dataset Queries with Context

### Overview
Execute complex queries across multiple datasets using context definitions that specify relationships, custom metrics, and business rules.

### Value Propositions
- **Natural Language Queries**: Ask questions across multiple datasets without knowing SQL joins
- **Context-Aware Intelligence**: Automatically applies relationships and business logic
- **Cross-Dataset Analysis**: Seamlessly query and join multiple datasets
- **Performance Optimization**: Generates optimized SQL with proper indexing
- **Business Logic Enforcement**: Applies filters, rules, and metrics from context
- **Query Reusability**: Save and share multi-dataset query patterns

### User Stories

#### US-4: Query with Context
**As a** data analyst
**I want to** execute queries using a context file
**So that** I can easily analyze data across multiple related datasets

**Acceptance Criteria:**
- [ ] Select context file when creating query
- [ ] Context provides available datasets, relationships, and metrics
- [ ] Auto-generated JOIN statements based on context relationships
- [ ] Access to custom metrics defined in context
- [ ] Apply business rules automatically
- [ ] Use pre-defined filters from context

#### US-5: Natural Language Multi-Dataset Queries
**As a** business user
**I want to** ask questions across multiple datasets in plain English
**So that** I can perform complex analysis without technical knowledge

**Acceptance Criteria:**
- [ ] NL query understands context relationships
- [ ] AI generates multi-dataset JOIN queries
- [ ] References custom metrics by name
- [ ] Applies business rules automatically
- [ ] Suggests relevant filters from context

### Query Types

#### 1. Natural Language Query
```json
{
  "query_type": "natural_language",
  "context_id": "uuid",
  "question": "Show me the top 10 customers by total revenue last year",
  "parameters": {
    "year": 2025
  },
  "options": {
    "limit": 10,
    "include_metrics": true,
    "apply_filters": true,
    "cache_result": true
  }
}
```

#### 2. Structured Query
```json
{
  "query_type": "structured",
  "context_id": "uuid",
  "datasets": ["customers_ds", "orders_ds"],
  "projections": {
    "fields": [
      "customers_ds.customer_name",
      "COUNT(orders_ds.order_id) as order_count",
      "SUM(orders_ds.order_amount) as total_revenue"
    ]
  },
  "relationships": ["customer_orders"],
  "filters": [
    {
      "dataset": "orders_ds",
      "condition": "order_date >= DATEADD(year, -1, TODAY())"
    }
  ],
  "sorting": {
    "field": "total_revenue",
    "order": "desc"
  },
  "limit": 10
}
```

#### 3. Metric-Based Aggregation Query
```json
{
  "query_type": "metric_aggregation",
  "context_id": "uuid",
  "metrics": [
    "total_revenue",
    "avg_order_value",
    "customer_count"
  ],
  "dimensions": {
    "fields": ["customers_ds.region", "orders_ds.product_category"]
  },
  "filters": {
    "active_customers": {},
    "recent_orders": {
      "days": 90
    }
  },
  "time_period": {
    "field": "orders_ds.order_date",
    "period": "month",
    "range": {
      "start": "2025-01-01",
      "end": "2025-12-31"
    }
  }
}
```

### API Endpoints (Multi-Dataset)

#### 1. Execute Multi-Dataset Query
```http
POST /api/queries/execute
Authorization: Bearer <token>

Request:
{
  "query_type": "natural_language",
  "context_id": "uuid",
  "question": "Show me the top 10 customers by total revenue last year"
}

Response: 200 OK
{
  "status": "success",
  "data": {
    "query_id": "uuid",
    "context_id": "uuid",
    "question": "Show me the top 10 customers by total revenue last year",
    "sql_query": "SELECT c.customer_name, SUM(o.order_amount) as total_revenue FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_date >= DATE('2025-01-01') GROUP BY c.customer_id, c.customer_name ORDER BY total_revenue DESC LIMIT 10",
    "execution_time_ms": 245,
    "rows_returned": 10,
    "columns": [
      {
        "name": "customer_name",
        "type": "string"
      },
      {
        "name": "total_revenue",
        "type": "float",
        "format": "$,.2f"
      }
    ],
    "rows": [
      {
        "customer_name": "Acme Corp",
        "total_revenue": 125000.50
      }
    ],
    "used_relationships": ["customer_orders"],
    "used_metrics": ["total_revenue"],
    "cache_info": {
      "cached": false,
      "expires_in_seconds": 3600
    }
  }
}
```

#### 2. Execute Structured Query
```http
POST /api/queries/structured
Authorization: Bearer <token>

Request:
{
  "context_id": "uuid",
  "datasets": ["customers_ds", "orders_ds"],
  "projections": {
    "fields": [
      "customers_ds.customer_name",
      "total_revenue"
    ]
  },
  "relationships": ["customer_orders"],
  "filters": [
    {
      "dataset": "orders_ds",
      "column": "order_date",
      "operator": ">=",
      "value": "2025-01-01"
    }
  ],
  "aggregations": {
    "group_by": ["customers_ds.customer_id", "customers_ds.customer_name"],
    "metrics": ["total_revenue"]
  },
  "sorting": {
    "field": "total_revenue",
    "order": "desc"
  },
  "limit": 10
}
```

#### 3. Save Query Template
```http
POST /api/queries/save
Authorization: Bearer <token>

Request:
{
  "name": "Top Customers by Revenue",
  "description": "Shows top N customers by total revenue",
  "context_id": "uuid",
  "query_definition": {
    "query_type": "natural_language",
    "question": "Show me the top {limit} customers by total revenue",
    "parameters": [
      {
        "name": "limit",
        "type": "integer",
        "default": 10
      }
    ]
  },
  "refresh_frequency": "daily",
  "is_public": false
}

Response: 201 Created
{
  "template_id": "uuid",
  "name": "Top Customers by Revenue",
  "created_at": "2026-01-26T14:30:00Z"
}
```

#### 4. Execute Query Template
```http
POST /api/queries/templates/{template_id}/execute
Authorization: Bearer <token>

Request:
{
  "parameters": {
    "limit": 20
  }
}
```

#### 5. Get Query Explanation
```http
POST /api/queries/explain
Authorization: Bearer <token>

Request:
{
  "context_id": "uuid",
  "question": "Show me the top 10 customers by total revenue last year"
}

Response: 200 OK
{
  "original_question": "Show me the top 10 customers by total revenue last year",
  "interpretation": {
    "intent": "aggregation",
    "metric": "total_revenue",
    "dimension": "customer",
    "sort_order": "descending",
    "limit": 10,
    "time_filter": "last_year"
  },
  "sql_query": "...",
  "execution_plan": {
    "steps": [
      {
        "step": 1,
        "operation": "Table Scan",
        "table": "customers",
        "estimated_rows": 10000
      },
      {
        "step": 2,
        "operation": "Join",
        "join_type": "LEFT OUTER JOIN",
        "tables": "customers, orders"
      }
    ],
    "estimated_execution_time_ms": 250
  },
  "applied_contexts": {
    "relationships": ["customer_orders"],
    "metrics": ["total_revenue"],
    "filters": ["last_year"]
  }
}
```

#### 6. Get Query History
```http
GET /api/query/history?context_id=uuid&skip=0&limit=50
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
  }
]
```

---

## Architecture

### Query Execution Flow

```
User Input (SQL/NL/Pandas) → Query Engine
         │
         ▼
    Single Dataset? ──Yes──> Load Dataset
         │                        ↓
         No                  Execute Query
         │                        ↓
         ▼                   Return Results
    Load Context
         │
         ├─→ Parse Context (relationships, metrics, rules)
         │
         ├─→ Load Multiple Datasets
         │
         ├─→ Resolve Relationships (auto-JOIN)
         │
         ├─→ Expand Metrics (calculated fields)
         │
         ├─→ Apply Business Rules
         │
         ├─→ Apply Filters
         │
         ├─→ Generate Optimized SQL
         │
         ├─→ Execute Query
         │
         ├─→ Format Results (apply metric formats)
         │
         └─→ Return Results + Metadata
```

### Core Components

#### 1. QueryEngine (Base)
Handles single-dataset queries.

```python
class QueryEngine:
    async def execute_sql(
        self,
        df: pd.DataFrame,
        sql: str
    ) -> pd.DataFrame:
        """Execute SQL query using pandasql"""
        # Validate SQL (no DDL/DML)
        # Use pandasql.sqldf() to execute
        # Return result DataFrame

    async def execute_pandas_operations(
        self,
        df: pd.DataFrame,
        operations: List[dict]
    ) -> pd.DataFrame:
        """Execute chain of Pandas operations"""
        for op in operations:
            if op['type'] == 'filter':
                df = df.query(op['condition'])
            elif op['type'] == 'sort':
                df = df.sort_values(op['by'], ascending=op['ascending'])
            # ... other operations
        return df

    async def natural_language_to_sql(
        self,
        question: str,
        schema: dict
    ) -> str:
        """Convert natural language to SQL using LLM"""
        # Call LLMService.generate_sql_query()
        # Validate generated SQL
        # Return SQL
```

#### 2. MultiDatasetQueryEngine (Extends QueryEngine)
Handles context-aware multi-dataset queries.

```python
class MultiDatasetQueryEngine(QueryEngine):
    def __init__(self, context_service: ContextService):
        super().__init__()
        self.context_service = context_service
        self.parser = QueryParser()
        self.resolver = RelationshipResolver()
        self.generator = SQLGenerator()
        self.optimizer = QueryOptimizer()
        self.rules_engine = BusinessRulesEngine()
        self.cache = CacheManager()

    async def execute_with_context(
        self,
        user_id: UUID,
        context_id: UUID,
        query: Dict[str, Any]
    ) -> QueryResult:
        """Execute query with context awareness"""

        # 1. Load context
        context = await self.context_service.get_context(context_id, user_id)

        # 2. Parse query
        query_rep = self._parse_query(query, context)

        # 3. Validate query
        validation = await self._validate_query(query_rep, context)
        if not validation['valid']:
            raise QueryValidationError(validation['issues'])

        # 4. Resolve relationships (find join paths)
        join_path = self.resolver.find_join_path(
            query_rep.datasets,
            context
        )

        # 5. Generate SQL
        sql = self.generator.generate(query_rep, context, join_path)

        # 6. Expand metrics
        sql = self._expand_metrics(sql, context.get('metrics', []))

        # 7. Apply business rules
        sql = self.rules_engine.apply_rules(sql, context, query_rep.datasets)

        # 8. Apply filters
        if query.get('apply_filters'):
            sql = self._apply_context_filters(sql, context, query['apply_filters'])

        # 9. Optimize query
        sql = self.optimizer.optimize(sql, context)

        # 10. Check cache
        cache_key = self._hash_query(sql)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # 11. Execute query
        result = await self._execute_multi_dataset(sql, context)

        # 12. Format results
        formatted = self._format_results(result, context)

        # 13. Cache results
        await self.cache.set(cache_key, formatted, ttl=3600)

        # 14. Save to history
        await self._save_history(user_id, context_id, query, sql, result)

        return formatted
```

#### 3. QueryParser
Converts various query formats into standardized representation.

```python
class QueryParser:
    def parse_natural_language(
        self,
        question: str,
        context: Context
    ) -> QueryRepresentation:
        """Parse natural language question"""
        # Use LLM to extract:
        # - Intent (aggregation, filter, join, etc.)
        # - Entities (customers, orders, products)
        # - Metrics (revenue, count, average)
        # - Time filters (last year, this month)
        # - Grouping dimensions
        # Build structured representation

    def parse_structured(
        self,
        query_json: Dict
    ) -> QueryRepresentation:
        """Parse structured query format"""
        # Extract datasets, projections, filters
        # Validate structure
        # Build representation

    def parse_metric_aggregation(
        self,
        query_json: Dict
    ) -> QueryRepresentation:
        """Parse metric-based aggregation query"""
        # Extract metrics and dimensions
        # Build aggregation structure
```

#### 4. RelationshipResolver
Determines optimal paths through dataset relationships.

```python
class RelationshipResolver:
    def find_join_path(
        self,
        datasets: List[str],
        context: Context
    ) -> List[Relationship]:
        """Find optimal join path through datasets"""
        # Build graph from relationships
        # Use A* or Dijkstra to find shortest path
        # Detect circular dependencies
        # Return ordered list of joins

    def validate_relationships(
        self,
        relationships: List[str],
        context: Context
    ) -> ValidationResult:
        """Validate relationships"""
        # Check circular dependencies
        # Verify dataset references
        # Check column existence
```

#### 5. SQLGenerator
Generates optimized SQL from query representation.

```python
class SQLGenerator:
    def generate(
        self,
        query_rep: QueryRepresentation,
        context: Context,
        join_path: List[Relationship]
    ) -> str:
        """Generate optimized SQL"""
        # Build SELECT clause
        # Build FROM clause
        # Build JOIN clauses from join_path
        # Build WHERE clause
        # Build GROUP BY
        # Build ORDER BY
        # Build LIMIT
        return sql
```

#### 6. BusinessRulesEngine
Applies business rules and validation constraints.

```python
class BusinessRulesEngine:
    def apply_rules(
        self,
        sql: str,
        context: Context,
        datasets: List[str]
    ) -> str:
        """Apply business rules to query"""
        # Find applicable rules
        # Inject rule conditions into WHERE clause
        # Add validation checks
        return modified_sql

    def validate_rule_compliance(
        self,
        results: List[Dict],
        context: Context
    ) -> RuleComplianceReport:
        """Validate results against rules"""
        # Check each rule
        # Identify violations
        # Return report
```

#### 7. CacheManager
Multi-layer caching for performance.

```python
class CacheManager:
    async def get_cached_result(
        self,
        query_hash: str
    ) -> Optional[QueryResult]:
        """Get result from cache"""
        # Try in-memory cache
        # Try Redis
        # Check TTL
        return result if valid else None

    async def cache_result(
        self,
        query_hash: str,
        result: QueryResult,
        ttl_seconds: int
    ):
        """Cache query results"""
        # Store in Redis
        # Add to in-memory cache
        # Set TTL
```

### Database Schema

```sql
-- Queries table (updated with context support)
CREATE TABLE queries (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,  -- NULL for multi-dataset
    context_id UUID REFERENCES contexts(id) ON DELETE SET NULL,  -- NULL for single-dataset
    name VARCHAR(255),
    query_type VARCHAR(50) NOT NULL,  -- 'sql', 'natural_language', 'pandas', 'structured', 'metric_aggregation'
    original_input TEXT NOT NULL,
    generated_query TEXT,
    operations JSONB,
    result_preview JSONB,
    result_row_count INTEGER,
    execution_time_ms INTEGER,
    llm_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Query templates
CREATE TABLE query_templates (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    context_id UUID REFERENCES contexts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    query_definition JSONB NOT NULL,
    parameters JSONB,
    refresh_frequency VARCHAR(50),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Query execution history (with context tracking)
CREATE TABLE query_contexts (
    id UUID PRIMARY KEY,
    query_id UUID NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    context_id UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,
    used_relationships JSONB,
    used_metrics JSONB,
    used_filters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_queries_user_id ON queries(user_id);
CREATE INDEX idx_queries_dataset_id ON queries(dataset_id);
CREATE INDEX idx_queries_context_id ON queries(context_id);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX idx_query_templates_user_id ON query_templates(user_id);
CREATE INDEX idx_query_contexts_query ON query_contexts(query_id);
CREATE INDEX idx_query_contexts_context ON query_contexts(context_id);
```

---

## Implementation

### Phase 1: Single-Dataset Queries (Weeks 1-2)
- [x] Basic QueryEngine class
- [ ] SQL execution with pandasql
- [ ] Pandas operations support
- [ ] Natural language to SQL (LLM integration)
- [ ] Query validation
- [ ] Single-dataset API routes
- [ ] Query history

### Phase 2: Context Integration (Weeks 3-4)
- [ ] MultiDatasetQueryEngine class
- [ ] QueryParser implementation
- [ ] RelationshipResolver with graph algorithms
- [ ] SQLGenerator for multi-dataset queries
- [ ] Context-aware API routes

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] BusinessRulesEngine
- [ ] QueryOptimizer
- [ ] CacheManager with Redis
- [ ] Query templates
- [ ] Query explanation endpoint

### Phase 4: Polish & Performance (Week 7)
- [ ] Comprehensive error handling
- [ ] Performance optimization
- [ ] Caching strategy
- [ ] Testing (unit, integration, performance)

---

## Testing Strategy

### Unit Tests
```python
# Single-dataset tests
def test_sql_execution():
    engine = QueryEngine()
    df = create_test_dataframe()
    result = await engine.execute_sql(df, "SELECT * FROM df WHERE value > 100")
    assert len(result) > 0

# Multi-dataset tests
def test_relationship_resolver():
    resolver = RelationshipResolver()
    path = resolver.find_join_path(['customers_ds', 'orders_ds', 'products_ds'], context)
    assert len(path) == 2  # customers -> orders -> products

def test_circular_dependency_detection():
    resolver = RelationshipResolver()
    circular_context = create_circular_context()
    with pytest.raises(CircularDependencyError):
        resolver.find_join_path(['a_ds', 'b_ds'], circular_context)

def test_metric_expansion():
    engine = MultiDatasetQueryEngine()
    sql = "SELECT customer_name, total_revenue FROM customers"
    expanded = engine._expand_metrics(sql, context.metrics)
    assert "SUM(o.order_amount)" in expanded
```

### Integration Tests
- End-to-end single-dataset query execution
- End-to-end multi-dataset query execution
- Context-aware query with relationships
- Business rules application
- Caching behavior
- Query template execution

### Performance Tests
- Query execution time benchmarks
- Cache hit rate analysis
- Large dataset query performance
- Concurrent query execution
- Memory usage profiling

**Target Benchmarks:**
- Simple SELECT (single dataset): < 100ms
- Aggregations (single dataset): < 500ms
- Multi-dataset with 2 JOINs: < 1 second
- Multi-dataset with 4 JOINs: < 2 seconds
- Natural language translation: < 2 seconds

---

## Security Considerations

1. **SQL Injection Prevention**
   - No DDL/DML statements allowed
   - Parameterized queries
   - SQL parsing and validation

2. **Access Control**
   - Users can only query their own datasets
   - Context access validation
   - Row-level security enforced

3. **Resource Limits**
   - Query timeout (30 seconds default)
   - Max result rows (100,000)
   - Max join depth (10)
   - Memory limits

4. **Audit Logging**
   - Track all query execution
   - User and timestamp
   - Query text and results count

---

## Success Metrics

### Single-Dataset Queries
- Query execution success rate > 95%
- Average execution time < 1 second
- NL query accuracy > 80%

### Multi-Dataset Queries
- Context-aware query adoption > 40%
- Multi-dataset execution time < 3 seconds
- Join optimization effectiveness > 70%
- NL accuracy with context > 90%

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

3. **Visual Query Builder**
   - Drag-and-drop interface
   - No-code query creation
   - Visual joins and filters

4. **Scheduled Queries**
   - Run queries on schedule
   - Email results
   - Trigger alerts

---

## Documentation

- [ ] API documentation (Swagger)
- [ ] User guide with examples
- [ ] SQL reference guide
- [ ] Context query guide
- [ ] Natural language query tips
- [ ] This feature spec

---

**Last Updated:** 2026-01-26
**Version:** 2.0.0 (Merged single + multi-dataset)
