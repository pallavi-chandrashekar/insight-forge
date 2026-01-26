# Multi-Dataset Query Engine Feature

## 1. Overview

### Purpose and Value Proposition

The Multi-Dataset Query Engine enables users to perform complex queries across multiple datasets using natural language or structured query definitions. This engine leverages Context File definitions to understand dataset relationships, custom metrics, and business rules, allowing users to ask sophisticated analytical questions without writing SQL or understanding complex join logic.

**Key Value Propositions:**
- **Natural Language Queries**: Ask questions in plain English that are converted to optimized SQL
- **Context-Aware Intelligence**: Understands dataset relationships and business logic defined in context files
- **Cross-Dataset Analysis**: Seamlessly query and join multiple datasets with a single request
- **Performance Optimization**: Generates optimized SQL with proper indexing and caching strategies
- **Business Logic Enforcement**: Automatically applies filters, rules, and metrics from context definitions
- **Query Reusability**: Save and share frequently used query patterns across teams

### Key Capabilities

1. **Query Translation**: Convert natural language or structured requests to SQL
2. **Context Integration**: Automatically apply relationships, metrics, and filters from context files
3. **Join Optimization**: Intelligently determine optimal join paths through multiple datasets
4. **Caching Layer**: Cache query results and metadata for improved performance
5. **Query Validation**: Detect and prevent problematic queries (circular joins, missing datasets)
6. **Business Rules Application**: Enforce business rules and data quality constraints
7. **Result Formatting**: Format results according to context metric definitions
8. **Query History**: Track executed queries for audit and optimization purposes

### User Personas and Use Cases

#### Persona 1: Business Analyst (Susan)
**Background**: Needs to quickly analyze sales performance across multiple datasets.

**Use Cases**:
- "Show me top 10 customers by revenue in the last quarter"
- "Compare this month's sales with previous month, broken down by product category"
- "Which customers are at risk of churning based on reduced order frequency?"

#### Persona 2: Data Scientist (David)
**Background**: Builds predictive models requiring complex multi-dataset queries.

**Use Cases**:
- Query patient cohorts with specific treatment and outcome patterns
- Extract feature sets combining behavioral, transactional, and demographic data
- Aggregate time-series data across related datasets for model training

#### Persona 3: Financial Analyst (Maria)
**Background**: Analyzes portfolio performance and risk across multiple data sources.

**Use Cases**:
- "Calculate portfolio returns and volatility for all accounts above $500K"
- "Identify concentrated positions across the entire book"
- "Show dividend income by security type for the fiscal year"

#### Persona 4: Executive (Robert)
**Background**: Needs executive dashboards and KPI reporting.

**Use Cases**:
- Monthly revenue by region and product line
- Customer acquisition cost trends
- Employee productivity metrics

---

## 2. Query Types and Specifications

### 2.1 Natural Language Query Format

```json
{
  "query_type": "natural_language",
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
  "question": "Show me the top 10 customers by total revenue last year",
  "parameters": {
    "year": 2025
  },
  "options": {
    "limit": 10,
    "include_metrics": true,
    "apply_filters": true,
    "cache_result": true,
    "timeout_seconds": 30
  }
}
```

**Processing Steps**:
1. Validate context existence and user access
2. Extract entities and intent from question
3. Map entities to datasets and columns
4. Build query structure using context relationships
5. Generate optimized SQL
6. Execute query with performance monitoring
7. Format results according to context metrics
8. Cache results if enabled

### 2.2 Structured Query Format

```json
{
  "query_type": "structured",
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
  "datasets": ["customers_ds", "orders_ds"],
  "projections": {
    "fields": [
      "customers_ds.customer_name",
      "COUNT(orders_ds.order_id) as order_count",
      "SUM(orders_ds.order_amount) as total_revenue"
    ]
  },
  "relationships": ["customer_orders"],
  "aggregations": {
    "group_by": ["customers_ds.customer_id", "customers_ds.customer_name"]
  },
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
  "limit": 10,
  "options": {
    "cache_result": true,
    "timeout_seconds": 30
  }
}
```

### 2.3 Metric-Based Query Format

```json
{
  "query_type": "metric_aggregation",
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
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

---

## 3. API Endpoints

### 3.1 Execute Natural Language Query

**Endpoint**: `POST /api/queries/execute`

**Description**: Execute a natural language query against multiple datasets.

**Authentication**: Required (JWT)

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "query_type": "natural_language",
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
  "question": "Show me the top 10 customers by total revenue last year",
  "parameters": {
    "year": 2025
  },
  "options": {
    "limit": 10,
    "explain": false,
    "timeout_seconds": 30
  }
}
```

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "query_id": "q1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
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
      },
      {
        "customer_name": "Global Industries",
        "total_revenue": 98765.00
      }
    ],
    "cache_info": {
      "cached": false,
      "cache_key": "q_f1a2b3c4_hash123",
      "expires_in_seconds": 3600
    }
  }
}
```

**Error Response (Invalid Context - 404)**:
```json
{
  "status": "error",
  "error": {
    "code": "CONTEXT_NOT_FOUND",
    "message": "Context not found or access denied",
    "details": {
      "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c"
    }
  }
}
```

**Error Response (Query Validation Failed - 422)**:
```json
{
  "status": "error",
  "error": {
    "code": "QUERY_VALIDATION_ERROR",
    "message": "Query validation failed",
    "details": {
      "issues": [
        {
          "type": "circular_dependency",
          "message": "Circular join detected: A->B->C->A"
        }
      ]
    }
  }
}
```

**Example curl**:
```bash
curl -X POST https://api.insightforge.com/api/queries/execute \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "natural_language",
    "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "question": "Show me the top 10 customers by total revenue last year"
  }'
```

### 3.2 Execute Structured Query

**Endpoint**: `POST /api/queries/structured`

**Description**: Execute a structured query using context relationships and metrics.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
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

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "query_id": "q1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "rows_returned": 10,
    "execution_time_ms": 312,
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
    ]
  }
}
```

### 3.3 Get Query History

**Endpoint**: `GET /api/queries/history`

**Description**: Get execution history for current user's queries.

**Authentication**: Required (JWT)

**Query Parameters**:
- `context_id` (UUID): Filter by context (optional)
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20)
- `sort_by` (string): "executed_at", "execution_time" (default: "executed_at")

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "queries": [
      {
        "query_id": "q1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
        "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
        "question": "Show me the top 10 customers by total revenue",
        "query_type": "natural_language",
        "executed_at": "2026-01-26T14:30:00Z",
        "execution_time_ms": 245,
        "rows_returned": 10,
        "status": "success"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 145,
      "total_pages": 8
    }
  }
}
```

### 3.4 Save Query as Reusable Template

**Endpoint**: `POST /api/queries/save`

**Description**: Save a query as a reusable template for future use.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "name": "Top Customers by Revenue",
  "description": "Shows top 10 customers by total revenue",
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
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
```

**Response (Success - 201 Created)**:
```json
{
  "status": "success",
  "data": {
    "template_id": "t1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "name": "Top Customers by Revenue",
    "created_at": "2026-01-26T14:30:00Z",
    "url": "/api/queries/templates/t1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c"
  }
}
```

### 3.5 Execute Saved Query Template

**Endpoint**: `POST /api/queries/templates/{template_id}/execute`

**Description**: Execute a previously saved query template with parameters.

**Authentication**: Required (JWT)

**Path Parameters**:
- `template_id` (UUID): Template identifier

**Request Body**:
```json
{
  "parameters": {
    "limit": 20
  }
}
```

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "query_id": "q1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "template_id": "t1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "rows_returned": 20,
    "execution_time_ms": 198,
    "rows": [...]
  }
}
```

### 3.6 Get Query Explanation

**Endpoint**: `POST /api/queries/explain`

**Description**: Get explanation of how a natural language query will be executed.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
  "question": "Show me the top 10 customers by total revenue last year"
}
```

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "original_question": "Show me the top 10 customers by total revenue last year",
    "interpretation": {
      "intent": "aggregation",
      "metric": "total_revenue",
      "dimension": "customer",
      "sort_order": "descending",
      "limit": 10,
      "time_filter": "last_year"
    },
    "sql_query": "SELECT c.customer_name, SUM(o.order_amount) as total_revenue FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_date >= DATE('2025-01-01') GROUP BY c.customer_id, c.customer_name ORDER BY total_revenue DESC LIMIT 10",
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
          "tables": "customers, orders",
          "on_condition": "c.customer_id = o.customer_id"
        },
        {
          "step": 3,
          "operation": "Filter",
          "condition": "o.order_date >= '2025-01-01'"
        },
        {
          "step": 4,
          "operation": "Aggregate",
          "group_by": "customer_id, customer_name",
          "aggregates": ["SUM(order_amount)"]
        },
        {
          "step": 5,
          "operation": "Sort",
          "order_by": "total_revenue DESC"
        },
        {
          "step": 6,
          "operation": "Limit",
          "count": 10
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
}
```

---

## 4. Query Engine Architecture

### 4.1 Core Components

#### Query Parser
Converts natural language or structured queries into an internal query representation.

```python
class QueryParser:
    """Parses various query formats into standardized representation"""

    def parse_natural_language(self, question: str, context: Context) -> QueryRepresentation:
        """Parse natural language question"""
        # Extract intent, entities, and relationships
        # Map to datasets and columns
        # Build query structure

    def parse_structured(self, query_json: Dict) -> QueryRepresentation:
        """Parse structured query format"""
        # Validate structure
        # Extract datasets and relationships
        # Build query representation

    def parse_metric_aggregation(self, query_json: Dict) -> QueryRepresentation:
        """Parse metric-based aggregation query"""
        # Extract metrics and dimensions
        # Apply context-defined aggregations
        # Build query representation
```

#### Relationship Resolver
Determines optimal paths through dataset relationships.

```python
class RelationshipResolver:
    """Resolves and optimizes dataset join paths"""

    def find_join_path(
        self,
        from_dataset: str,
        to_dataset: str,
        context: Context
    ) -> List[Relationship]:
        """Find shortest path between datasets"""
        # Use graph algorithm (A*)
        # Consider join types and conditions
        # Detect circular dependencies
        # Return optimized path

    def validate_relationships(self, relationships: List[str], context: Context) -> ValidationResult:
        """Validate requested relationships exist and are valid"""
        # Check circular dependencies
        # Verify dataset references
        # Check column existence
```

#### SQL Generator
Generates optimized SQL from query representation.

```python
class SQLGenerator:
    """Generates optimized SQL from query representation"""

    def generate(
        self,
        query_rep: QueryRepresentation,
        context: Context,
        dataset_schemas: Dict[str, Schema]
    ) -> str:
        """Generate optimized SQL query"""
        # Build SELECT clause with projections
        # Build FROM clause with primary dataset
        # Build JOIN clauses using relationships
        # Build WHERE clause with filters
        # Build GROUP BY for aggregations
        # Build ORDER BY
        # Build LIMIT
        # Add query hints/comments

    def add_metrics(self, sql: str, metrics: List[Metric]) -> str:
        """Add context metrics to query"""
        # Inject metric expressions
        # Apply metric formatting
```

#### Query Optimizer
Optimizes query execution strategy.

```python
class QueryOptimizer:
    """Optimizes query execution"""

    def optimize(
        self,
        sql: str,
        context: Context,
        estimated_rows: Dict[str, int]
    ) -> str:
        """Optimize query for performance"""
        # Reorder joins for efficiency
        # Push down filters
        # Use database hints
        # Add indexes if needed
        # Estimate execution cost

    def estimate_execution_time(self, sql: str) -> int:
        """Estimate query execution time in milliseconds"""
        # Parse query structure
        # Estimate rows at each step
        # Calculate time based on operations
```

#### Business Rules Engine
Applies business rules and validation constraints.

```python
class BusinessRulesEngine:
    """Applies context business rules"""

    def apply_rules(
        self,
        sql: str,
        context: Context,
        datasets: List[str]
    ) -> str:
        """Apply business rules to query"""
        # Find applicable rules
        # Inject rule conditions
        # Check for conflicts
        # Add rule violations checks

    def validate_rule_compliance(
        self,
        results: List[Dict],
        context: Context
    ) -> RuleComplianceReport:
        """Validate results against business rules"""
        # Check each rule
        # Identify violations
        # Return compliance report
```

### 4.2 Caching Strategy

**Cache Layers**:

1. **Result Cache**: Full query results cached by query hash
   - TTL: 1 hour by default, configurable per context
   - Key: SHA256(sql_query + parameters)
   - Storage: Redis
   - Invalidation: Manual or TTL-based

2. **Metadata Cache**: Context definitions and schemas
   - TTL: 24 hours
   - Key: context_id + version
   - Storage: Redis + in-memory
   - Invalidation: On context update

3. **Execution Plan Cache**: Pre-computed execution plans
   - TTL: 7 days
   - Key: query_structure_hash
   - Storage: Database
   - Invalidation: On schema changes

```python
class CacheManager:
    """Manages multi-layer caching"""

    async def get_cached_result(self, query_hash: str) -> Optional[List[Dict]]:
        """Get result from cache"""
        # Try in-memory cache first
        # Try Redis
        # Check TTL
        # Return if valid

    async def cache_result(
        self,
        query_hash: str,
        results: List[Dict],
        ttl_seconds: int
    ):
        """Cache query results"""
        # Store in Redis
        # Add to in-memory cache
        # Set TTL

    async def invalidate_context_cache(self, context_id: UUID):
        """Invalidate cache for context changes"""
        # Clear related result cache entries
        # Clear metadata cache
        # Clear execution plans
```

---

## 5. Service Implementation

### 5.1 QueryExecutionService

**File**: `backend/app/services/query_execution_service.py`

```python
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.query import Query, QueryTemplate
from app.services.query_parser import QueryParser
from app.services.relationship_resolver import RelationshipResolver
from app.services.sql_generator import SQLGenerator
from app.services.query_optimizer import QueryOptimizer
from app.services.business_rules_engine import BusinessRulesEngine
from app.services.context_service import ContextService
from app.services.cache_manager import CacheManager
from app.core.exceptions import QueryExecutionError, QueryValidationError

class QueryExecutionService:
    """Service for executing multi-dataset queries"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = QueryParser()
        self.resolver = RelationshipResolver()
        self.generator = SQLGenerator()
        self.optimizer = QueryOptimizer()
        self.rules_engine = BusinessRulesEngine()
        self.context_service = ContextService(db)
        self.cache = CacheManager()

    async def execute_query(
        self,
        user_id: UUID,
        query_input: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a query (natural language, structured, or metric-based).

        Args:
            user_id: User executing the query
            query_input: Query definition (format depends on query_type)
            options: Execution options (cache, timeout, etc.)

        Returns:
            Query execution result with rows and metadata

        Raises:
            QueryValidationError: If query is invalid
            QueryExecutionError: If execution fails
        """
        options = options or {}
        timeout_seconds = options.get('timeout_seconds', 30)
        use_cache = options.get('cache_result', True)
        explain_only = options.get('explain', False)

        # Get context
        context_id = UUID(query_input.get('context_id'))
        context = await self.context_service.get_context(context_id, user_id)

        # Parse query based on type
        query_type = query_input.get('query_type', 'natural_language')

        if query_type == 'natural_language':
            query_rep = self.parser.parse_natural_language(
                query_input.get('question'),
                context
            )
        elif query_type == 'structured':
            query_rep = self.parser.parse_structured(query_input)
        elif query_type == 'metric_aggregation':
            query_rep = self.parser.parse_metric_aggregation(query_input)
        else:
            raise QueryValidationError(f"Unknown query type: {query_type}")

        # Validate query
        validation_result = await self._validate_query(query_rep, context, user_id)
        if not validation_result['valid']:
            raise QueryValidationError(
                "Query validation failed",
                validation_result['issues']
            )

        # Generate SQL
        sql_query = self.generator.generate(query_rep, context)

        # Apply business rules
        sql_query = self.rules_engine.apply_rules(sql_query, context, query_rep.datasets)

        # Optimize query
        sql_query = self.optimizer.optimize(sql_query, context)

        # Generate execution plan
        execution_plan = self.optimizer.get_execution_plan(sql_query)

        if explain_only:
            return {
                'sql_query': sql_query,
                'execution_plan': execution_plan,
                'estimated_execution_time_ms': execution_plan.get('estimated_time_ms', 0)
            }

        # Check cache
        query_hash = self._hash_query(sql_query, query_input.get('parameters', {}))
        if use_cache:
            cached_result = await self.cache.get_cached_result(query_hash)
            if cached_result:
                return {
                    'query_id': self._generate_query_id(),
                    'rows': cached_result,
                    'cached': True,
                    'execution_time_ms': 0
                }

        # Execute query with timeout
        import asyncio
        import time

        start_time = time.time()
        try:
            rows = await asyncio.wait_for(
                self._execute_sql(sql_query),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            raise QueryExecutionError(f"Query execution timeout after {timeout_seconds}s")

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Format results
        formatted_rows = self._format_results(rows, query_rep, context)

        # Cache results
        if use_cache:
            await self.cache.cache_result(
                query_hash,
                formatted_rows,
                context.get('settings', {}).get('cache_ttl_seconds', 3600)
            )

        # Save to history
        await self._save_query_history(
            user_id,
            context_id,
            query_type,
            query_input.get('question') or str(query_input),
            sql_query,
            len(formatted_rows),
            execution_time_ms
        )

        return {
            'query_id': self._generate_query_id(),
            'sql_query': sql_query,
            'rows': formatted_rows,
            'execution_time_ms': execution_time_ms,
            'rows_returned': len(formatted_rows),
            'cached': False
        }

    async def _validate_query(
        self,
        query_rep: 'QueryRepresentation',
        context: Dict[str, Any],
        user_id: UUID
    ) -> Dict[str, Any]:
        """Validate query structure and references"""
        issues = []

        # Check datasets exist in context
        context_datasets = {ds['id'] for ds in context.get('datasets', [])}
        for dataset in query_rep.datasets:
            if dataset not in context_datasets:
                issues.append({
                    'type': 'missing_dataset',
                    'dataset': dataset,
                    'message': f"Dataset '{dataset}' not found in context"
                })

        # Check relationships exist
        context_rels = {rel['id'] for rel in context.get('relationships', [])}
        for rel_id in query_rep.relationships:
            if rel_id not in context_rels:
                issues.append({
                    'type': 'missing_relationship',
                    'relationship': rel_id,
                    'message': f"Relationship '{rel_id}' not found in context"
                })

        # Check for circular dependencies
        if self.resolver.has_circular_dependency(query_rep.relationships, context):
            issues.append({
                'type': 'circular_dependency',
                'message': 'Circular join dependency detected'
            })

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    async def _execute_sql(self, sql: str) -> List[Dict]:
        """Execute SQL query against database"""
        result = await self.db.execute(sql)
        rows = result.fetchall()
        return [dict(row) for row in rows]

    def _format_results(
        self,
        rows: List[Dict],
        query_rep: 'QueryRepresentation',
        context: Dict[str, Any]
    ) -> List[Dict]:
        """Format results according to context metric definitions"""
        formatted = []

        for row in rows:
            formatted_row = {}
            for key, value in row.items():
                # Find metric definition
                metric = next(
                    (m for m in context.get('metrics', [])
                     if m['id'] == key or m['name'] == key),
                    None
                )

                # Apply formatting if metric found
                if metric and metric.get('format'):
                    formatted_row[key] = self._format_value(
                        value,
                        metric.get('data_type'),
                        metric.get('format')
                    )
                else:
                    formatted_row[key] = value

            formatted.append(formatted_row)

        return formatted

    def _format_value(self, value: Any, data_type: str, format_spec: str) -> str:
        """Format value according to specification"""
        if value is None:
            return None

        if data_type == 'float' and '$' in format_spec:
            # Currency formatting
            return f"${value:,.2f}".replace('.00', '') if format_spec == '$' else f"${value:{format_spec}}"
        elif data_type == 'float' and '%' in format_spec:
            # Percentage
            return f"{value:.2f}%"

        return str(value)

    def _hash_query(self, sql: str, parameters: Dict) -> str:
        """Hash query for caching key"""
        import hashlib
        import json

        query_str = sql + json.dumps(parameters, sort_keys=True)
        return hashlib.sha256(query_str.encode()).hexdigest()

    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        import uuid
        return str(uuid.uuid4())

    async def _save_query_history(
        self,
        user_id: UUID,
        context_id: UUID,
        query_type: str,
        question: str,
        sql_query: str,
        rows_returned: int,
        execution_time_ms: int
    ):
        """Save query to execution history"""
        query_record = Query(
            user_id=user_id,
            context_id=context_id,
            query_type=query_type,
            question=question,
            sql_query=sql_query,
            rows_returned=rows_returned,
            execution_time_ms=execution_time_ms
        )

        self.db.add(query_record)
        await self.db.commit()
```

### 5.2 QueryTemplate Management

**File**: `backend/app/services/query_template_service.py`

```python
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query import QueryTemplate
from app.core.exceptions import QueryTemplateNotFoundError

class QueryTemplateService:
    """Service for managing reusable query templates"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(
        self,
        user_id: UUID,
        name: str,
        description: str,
        context_id: UUID,
        query_definition: Dict[str, Any],
        refresh_frequency: Optional[str] = None,
        is_public: bool = False
    ) -> QueryTemplate:
        """Create a reusable query template"""
        template = QueryTemplate(
            user_id=user_id,
            name=name,
            description=description,
            context_id=context_id,
            query_definition=query_definition,
            refresh_frequency=refresh_frequency,
            is_public=is_public
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def execute_template(
        self,
        template_id: UUID,
        user_id: UUID,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a query template with parameters"""
        template = await self._get_template(template_id, user_id)

        # Replace parameters in query definition
        query_def = self._substitute_parameters(
            template.query_definition,
            parameters or {}
        )

        # Execute using QueryExecutionService
        from app.services.query_execution_service import QueryExecutionService
        exec_service = QueryExecutionService(self.db)

        return await exec_service.execute_query(user_id, query_def)

    async def list_templates(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List saved query templates"""
        # Query database with pagination
        # Return templates and pagination info
        pass

    def _substitute_parameters(
        self,
        query_def: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Substitute parameters into query definition"""
        # Handle string substitution for question text
        # Replace {param_name} with actual values
        # Type-convert parameters as needed
        pass
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Test Coverage Areas**:
- Query Parser (natural language, structured, metric-based)
- Relationship Resolver (join path finding, circular dependency detection)
- SQL Generator (correct SQL syntax for various query types)
- Query Optimizer (optimization logic, estimate accuracy)
- Business Rules Engine (rule application, constraint validation)
- Cache Manager (cache hit/miss, TTL, invalidation)

**Sample Unit Tests**:

```python
def test_parser_natural_language_top_customers():
    """Test parsing simple natural language query"""
    parser = QueryParser()
    question = "Show me the top 10 customers by revenue"
    result = parser.parse_natural_language(question, mock_context)

    assert result.intent == 'aggregation'
    assert result.metric == 'total_revenue'
    assert result.limit == 10

def test_resolver_finds_shortest_path():
    """Test relationship resolver finds optimal join path"""
    resolver = RelationshipResolver()
    path = resolver.find_join_path('customers_ds', 'products_ds', mock_context)

    assert len(path) == 2  # customers -> orders -> products
    assert path[0].id == 'customer_orders'
    assert path[1].id == 'order_products'

def test_circular_dependency_detection():
    """Test detection of circular join dependencies"""
    resolver = RelationshipResolver()
    circular_context = create_circular_context()

    with pytest.raises(CircularDependencyError):
        resolver.find_join_path('a_ds', 'b_ds', circular_context)

def test_sql_generator_correct_join_syntax():
    """Test SQL generator creates correct JOIN clauses"""
    generator = SQLGenerator()
    query_rep = create_simple_query_representation()
    sql = generator.generate(query_rep, mock_context)

    assert 'LEFT JOIN' in sql
    assert 'ON c.customer_id = o.customer_id' in sql

def test_business_rules_applied():
    """Test business rules are applied to queries"""
    rules_engine = BusinessRulesEngine()
    sql = "SELECT * FROM customers c JOIN orders o ON c.customer_id = o.customer_id"

    applied_sql = rules_engine.apply_rules(sql, mock_context, ['customers_ds', 'orders_ds'])

    assert 'age >= 18' in applied_sql  # Adult patient rule
    assert 'valid_age' in applied_sql  # Rule name or ID
```

### 6.2 Integration Tests

- End-to-end query execution for various query types
- Caching behavior and invalidation
- Query history tracking
- Template execution with parameters
- Error handling and edge cases

### 6.3 Performance Tests

- Query execution time benchmarks
- Cache hit rate analysis
- Large dataset query performance
- Concurrent query execution
- Memory usage profiling

---

## 7. Error Handling and Edge Cases

### 7.1 Query Validation Errors

```
- Invalid context ID
- Missing required datasets
- Broken relationships
- Circular dependencies
- Non-existent columns
- Type mismatches in filters
- Invalid metric expressions
```

### 7.2 Execution Errors

```
- Query timeout
- Database connection failures
- SQL syntax errors
- Resource exhaustion
- Permission denied on datasets
```

### 7.3 Edge Cases

```
- Empty result sets
- NULL values in results
- Very large result sets
- Parameterized queries with missing parameters
- Nested aggregations
- Self-joins
- Multiple paths between datasets
```

---

## 8. Security Considerations

1. **Access Control**: Users can only query contexts they own or have access to
2. **SQL Injection Prevention**: Parameterized queries for all dynamic values
3. **Data Masking**: Apply context-defined filters for PII and sensitive data
4. **Audit Logging**: Track all query execution with user and timestamp
5. **Rate Limiting**: Prevent query flood attacks
6. **Query Complexity Limits**: Reject overly complex queries (too many joins, large result sets)

---

## 9. Deployment and Configuration

### 9.1 Environment Variables

```bash
QUERY_ENGINE_CACHE_ENABLED=true
QUERY_ENGINE_CACHE_TTL_SECONDS=3600
QUERY_ENGINE_MAX_RESULT_ROWS=100000
QUERY_ENGINE_TIMEOUT_SECONDS=30
QUERY_ENGINE_MAX_JOIN_DEPTH=10
QUERY_ENGINE_ENABLE_QUERY_HISTORY=true
```

### 9.2 Database Migrations

Create indexes for optimal query performance:

```sql
CREATE INDEX idx_query_history_user_context
ON query_history(user_id, context_id, executed_at DESC);

CREATE INDEX idx_query_template_user
ON query_templates(user_id, name);
```

---

## 10. Implementation Checklist

- [ ] Implement QueryParser with NLP support
- [ ] Implement RelationshipResolver with graph algorithms
- [ ] Implement SQLGenerator with multiple query type support
- [ ] Implement QueryOptimizer with cost estimation
- [ ] Implement BusinessRulesEngine
- [ ] Implement CacheManager with Redis integration
- [ ] Create API endpoints for query execution
- [ ] Create API endpoints for query templates
- [ ] Create database models for Query and QueryTemplate
- [ ] Implement comprehensive error handling
- [ ] Write unit tests (minimum 80% coverage)
- [ ] Write integration tests
- [ ] Write performance benchmarks
- [ ] Implement query history logging
- [ ] Implement access control checks
- [ ] Document API with OpenAPI/Swagger
- [ ] Load testing and optimization
- [ ] Deploy to staging environment
- [ ] User acceptance testing
- [ ] Deploy to production

---

## Change Log

- v1.0.0 (2026-01-26): Initial release
  - Natural language query support
  - Structured query support
  - Query template system
  - Multi-level caching
  - Business rules enforcement
  - Query history tracking
