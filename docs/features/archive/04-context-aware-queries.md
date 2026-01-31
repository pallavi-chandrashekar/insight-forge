# Feature: Context-Aware Multi-Dataset Queries

## Overview
Enable users to execute queries across multiple datasets using context files that define relationships, metrics, and business rules. This feature integrates Context File Management with the Query Execution Engine.

## Status
🚧 **TO BE IMPLEMENTED**

## Dependencies
- ✅ Feature 01: Data Upload & Management
- 🚧 Feature 02: Query Execution
- ✅ Feature 00: Context File Management

---

## User Stories

### US-1: Query with Context
**As a** data analyst
**I want to** execute queries using a context file
**So that** I can easily analyze data across multiple related datasets

**Acceptance Criteria:**
- [ ] Select context file when creating a query
- [ ] Context provides available datasets, relationships, and metrics
- [ ] Auto-generated JOIN statements based on context relationships
- [ ] Access to custom metrics defined in context
- [ ] Apply business rules automatically
- [ ] Use pre-defined filters from context

### US-2: Natural Language with Context
**As a** business user
**I want to** ask natural language questions with context awareness
**So that** I can query multiple datasets without knowing SQL

**Acceptance Criteria:**
- [ ] NL query understands context relationships
- [ ] AI generates multi-dataset JOIN queries
- [ ] References custom metrics by name
- [ ] Applies business rules automatically
- [ ] Suggests relevant filters from context

### US-3: Context-Based Query Suggestions
**As a** user
**I want to** get query suggestions based on context
**So that** I can discover useful insights quickly

**Acceptance Criteria:**
- [ ] Show common query patterns for the context
- [ ] Suggest queries using custom metrics
- [ ] Recommend aggregations based on relationships
- [ ] Display example queries from context documentation

---

## Integration Points

### With Context File Management
- Load context file before query execution
- Parse relationships to generate JOINs
- Make custom metrics available as calculated fields
- Apply business rules for validation
- Provide filters as query modifiers

### With Query Engine
- Extend SQL generation to include multi-dataset JOINs
- Add support for custom metric expressions
- Validate queries against business rules
- Apply context filters automatically

### With LLM Service
- Include context schema in prompts
- Describe relationships and metrics to AI
- Use context documentation to improve accuracy
- Generate context-aware SQL from natural language

---

## Query Flow with Context

```
User selects context → Load context definition
         │
         ▼
    Display available:
    - Datasets (from context)
    - Relationships (auto-JOIN)
    - Metrics (calculated fields)
    - Filters (pre-defined)
         │
         ▼
    User writes query OR natural language
         │
         ├─→ SQL Query:
         │    ├─→ Replace metric references with expressions
         │    ├─→ Auto-generate JOINs from relationships
         │    ├─→ Apply business rules
         │    └─→ Execute query
         │
         ├─→ Natural Language:
         │    ├─→ Send to LLM with context schema
         │    ├─→ LLM generates SQL using context
         │    ├─→ Validate against business rules
         │    └─→ Execute generated SQL
         │
         └─→ Return results with context metadata
```

---

## API Endpoints

### 1. Execute Query with Context
```http
POST /api/query/execute-with-context
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "context_id": "uuid",
  "query_type": "sql",  // or "natural_language"
  "query": "SELECT customer_name, total_revenue FROM customers",
  "apply_filters": ["active_customers"],  // Optional: apply context filters
  "use_metrics": ["total_revenue", "avg_order_value"],  // Optional: reference metrics
  "save": true,
  "name": "Customer Revenue Analysis"
}

Response: 200 OK
{
  "id": "query-uuid",
  "context_id": "uuid",
  "context_name": "ecommerce_basic",
  "query_type": "sql",
  "original_input": "SELECT customer_name, total_revenue FROM customers",
  "generated_query": "SELECT c.customer_name, SUM(o.order_amount) as total_revenue FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE c.last_order_date >= DATE('now', '-90 days') GROUP BY c.customer_name",
  "used_relationships": ["customer_orders"],
  "used_metrics": ["total_revenue"],
  "used_filters": ["active_customers"],
  "business_rules_applied": [
    {
      "rule_id": "valid_customer",
      "status": "passed"
    }
  ],
  "result_preview": {...},
  "execution_time_ms": 150
}
```

### 2. Natural Language with Context
```http
POST /api/query/natural-language-with-context
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "context_id": "uuid",
  "question": "What are the top 5 customers by revenue in the last quarter?",
  "apply_filters": ["active_customers"],
  "save": true
}

Response: 200 OK
{
  "id": "query-uuid",
  "context_id": "uuid",
  "context_name": "ecommerce_basic",
  "query_type": "natural_language",
  "original_input": "What are the top 5 customers by revenue in the last quarter?",
  "generated_query": "SELECT c.customer_name, SUM(o.order_amount) as total_revenue FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE c.last_order_date >= DATE('now', '-90 days') AND o.order_date >= DATE('now', '-90 days') GROUP BY c.customer_name ORDER BY total_revenue DESC LIMIT 5",
  "explanation": "Query uses customer_orders relationship to join customers and orders, applies active_customers filter, calculates total_revenue metric, and returns top 5",
  "used_relationships": ["customer_orders"],
  "used_metrics": ["total_revenue"],
  "used_filters": ["active_customers"],
  "result_preview": {...}
}
```

### 3. Get Context Query Suggestions
```http
GET /api/query/context-suggestions/{context_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "context_id": "uuid",
  "context_name": "ecommerce_basic",
  "suggestions": [
    {
      "id": "top_customers",
      "title": "Top Customers by Revenue",
      "description": "Find highest spending customers",
      "query": "SELECT customer_name, total_revenue FROM customers ORDER BY total_revenue DESC LIMIT 10",
      "uses_relationships": ["customer_orders"],
      "uses_metrics": ["total_revenue"]
    },
    {
      "id": "product_performance",
      "title": "Product Performance",
      "description": "Analyze product sales",
      "query": "SELECT product_name, COUNT(*) as order_count FROM orders JOIN products USING (product_id) GROUP BY product_name",
      "uses_relationships": ["order_products"]
    }
  ]
}
```

---

## Technical Implementation

### Backend Changes

#### Update QueryEngine

```python
class QueryEngine:
    def __init__(self, context_service: ContextService):
        self.context_service = context_service

    async def execute_with_context(
        self,
        user_id: UUID,
        context_id: UUID,
        query: str,
        query_type: str,
        apply_filters: List[str] = None,
        use_metrics: List[str] = None
    ) -> QueryResult:
        """Execute query with context awareness"""

        # Load context
        context = await self.context_service.get_context(
            context_id, user_id, resolve_datasets=True
        )

        # Load all datasets from context
        datasets = await self._load_context_datasets(context, user_id)

        # Process query based on type
        if query_type == "sql":
            # Expand metric references
            query = self._expand_metrics(query, context.get('metrics', []))

            # Generate JOINs from relationships
            query = self._add_relationships(query, context.get('relationships', []))

            # Apply filters
            if apply_filters:
                query = self._apply_context_filters(
                    query,
                    context.get('filters', []),
                    apply_filters
                )

            # Execute on joined dataframe
            df = self._join_datasets(datasets, context.get('relationships', []))
            result_df = await self.execute_sql(df, query)

        elif query_type == "natural_language":
            # Generate SQL with context
            result = await self._natural_language_with_context(
                query,
                context,
                datasets,
                apply_filters
            )
            result_df = result['dataframe']
            query = result['generated_sql']

        # Apply business rules for validation
        self._validate_business_rules(result_df, context.get('business_rules', []))

        # Save query with context linkage
        query_record = await self._save_query_with_context(
            user_id=user_id,
            context_id=context_id,
            query_type=query_type,
            original_input=query,
            result_df=result_df
        )

        return query_record

    def _expand_metrics(
        self,
        query: str,
        metrics: List[Dict[str, Any]]
    ) -> str:
        """Replace metric names with their expressions"""
        for metric in metrics:
            metric_name = metric['id']
            expression = metric['expression']
            # Replace references to metric_name with expression
            query = query.replace(metric_name, f"({expression})")
        return query

    def _add_relationships(
        self,
        query: str,
        relationships: List[Dict[str, Any]]
    ) -> str:
        """Auto-generate JOIN clauses"""
        # Parse query to find referenced tables
        # Add appropriate JOINs based on relationships
        # Return modified query
        pass

    def _apply_context_filters(
        self,
        query: str,
        filters: List[Dict[str, Any]],
        filter_ids: List[str]
    ) -> str:
        """Apply pre-defined filters from context"""
        conditions = []
        for filter_def in filters:
            if filter_def['id'] in filter_ids:
                conditions.append(filter_def['condition'])

        if conditions:
            # Add WHERE clause or AND conditions
            filter_clause = " AND ".join(conditions)
            if "WHERE" in query.upper():
                query += f" AND {filter_clause}"
            else:
                query += f" WHERE {filter_clause}"

        return query

    def _join_datasets(
        self,
        datasets: Dict[str, pd.DataFrame],
        relationships: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Join datasets based on relationships"""
        if not relationships:
            # Single dataset - return first one
            return list(datasets.values())[0]

        # Build join order
        join_order = self._compute_join_order(relationships)

        # Start with first dataset
        result_df = datasets[join_order[0]['left_dataset']]

        # Apply joins sequentially
        for rel in join_order:
            left_ds_id = rel['left_dataset']
            right_ds_id = rel['right_dataset']
            join_type = rel['join_type']

            # Get dataframes
            left_df = result_df if left_ds_id == join_order[0]['left_dataset'] else datasets[left_ds_id]
            right_df = datasets[right_ds_id]

            # Build join condition
            on_conditions = []
            for cond in rel['conditions']:
                if cond['condition_type'] == 'on':
                    on_conditions.append(
                        (cond['left_column'], cond['right_column'])
                    )

            # Perform join
            result_df = pd.merge(
                left_df,
                right_df,
                left_on=[c[0] for c in on_conditions],
                right_on=[c[1] for c in on_conditions],
                how=join_type
            )

        return result_df

    async def _natural_language_with_context(
        self,
        question: str,
        context: Dict[str, Any],
        datasets: Dict[str, pd.DataFrame],
        apply_filters: List[str] = None
    ) -> Dict[str, Any]:
        """Generate SQL from natural language using context"""

        # Build enhanced prompt with context
        context_description = self._build_context_description(context)

        prompt = f"""
You are a SQL expert. Generate a SQL query based on the user's question.

Context: {context['name']} - {context['description']}

Available Datasets:
{self._format_datasets(context['datasets'])}

Relationships:
{self._format_relationships(context['relationships'])}

Custom Metrics:
{self._format_metrics(context['metrics'])}

Available Filters:
{self._format_filters(context['filters'])}

User Question: {question}

Generate a SQL query that:
1. Uses appropriate JOINs based on relationships
2. References custom metrics by their expressions
3. Applies relevant filters
4. Answers the user's question accurately

Return only the SQL query.
"""

        # Call LLM
        generated_sql = await self.llm_service.generate_sql_query(
            question=question,
            schema=context,
            context_prompt=prompt
        )

        # Apply filters if specified
        if apply_filters:
            generated_sql = self._apply_context_filters(
                generated_sql,
                context.get('filters', []),
                apply_filters
            )

        # Execute query
        df = self._join_datasets(datasets, context.get('relationships', []))
        result_df = await self.execute_sql(df, generated_sql)

        return {
            'generated_sql': generated_sql,
            'dataframe': result_df,
            'explanation': f"Query uses context '{context['name']}' with relationships and metrics"
        }

    def _validate_business_rules(
        self,
        df: pd.DataFrame,
        rules: List[Dict[str, Any]]
    ) -> None:
        """Validate query results against business rules"""
        for rule in rules:
            condition = rule['condition']
            severity = rule['severity']

            # Evaluate condition on dataframe
            # If severity is 'error' and validation fails, raise exception
            # If severity is 'warning', log warning
            pass
```

#### Update LLMService

```python
class LLMService:
    async def generate_sql_with_context(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate SQL query using context information"""

        system_prompt = f"""You are a SQL expert with knowledge of data relationships.

Context: {context['name']}
Description: {context['description']}

Datasets:
{self._format_context_datasets(context['datasets'])}

Relationships:
{self._format_context_relationships(context['relationships'])}

Custom Metrics:
{self._format_context_metrics(context['metrics'])}

Rules:
1. Use relationships to JOIN tables automatically
2. Reference custom metrics by their expressions
3. Handle NULLs appropriately
4. Generate efficient queries
5. Only use SELECT statements
"""

        user_prompt = f"""Question: {question}

Generate a SQL query to answer this question using the context above."""

        response = await self._call_claude(system_prompt, user_prompt)
        return self._clean_sql(response)
```

### Frontend Changes

#### Query Page with Context Selector

```typescript
// frontend/src/pages/Query.tsx

interface QueryPageProps {}

export function QueryPage() {
  const [contexts, setContexts] = useState<Context[]>([]);
  const [selectedContext, setSelectedContext] = useState<Context | null>(null);
  const [query, setQuery] = useState('');
  const [queryType, setQueryType] = useState<'sql' | 'natural_language'>('sql');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load available contexts
    api.get('/contexts').then(res => setContexts(res.data.contexts));
  }, []);

  const handleContextChange = async (contextId: string) => {
    // Load full context details
    const context = await api.get(`/contexts/${contextId}`);
    setSelectedContext(context.data);
  };

  const executeQuery = async () => {
    setLoading(true);
    try {
      const response = await api.post('/query/execute-with-context', {
        context_id: selectedContext?.context_id,
        query_type: queryType,
        query: query,
        apply_filters: selectedFilters,
        save: true
      });
      setResults(response.data);
    } catch (error) {
      console.error('Query execution failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-page">
      {/* Context Selector */}
      <div className="context-selector">
        <label>Select Context:</label>
        <select onChange={(e) => handleContextChange(e.target.value)}>
          <option value="">No Context (Single Dataset)</option>
          {contexts.map(ctx => (
            <option key={ctx.context_id} value={ctx.context_id}>
              {ctx.name} v{ctx.version}
            </option>
          ))}
        </select>
      </div>

      {/* Context Info Panel */}
      {selectedContext && (
        <div className="context-info">
          <h3>{selectedContext.name}</h3>
          <p>{selectedContext.description}</p>

          <div className="context-details">
            <div>
              <h4>Datasets ({selectedContext.datasets.length})</h4>
              <ul>
                {selectedContext.datasets.map(ds => (
                  <li key={ds.id}>{ds.name}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4>Available Metrics</h4>
              <ul>
                {selectedContext.metrics?.map(m => (
                  <li key={m.id} title={m.description}>
                    {m.name} - {m.expression}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4>Filters</h4>
              {selectedContext.filters?.map(f => (
                <label key={f.id}>
                  <input
                    type="checkbox"
                    checked={selectedFilters.includes(f.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedFilters([...selectedFilters, f.id]);
                      } else {
                        setSelectedFilters(selectedFilters.filter(id => id !== f.id));
                      }
                    }}
                  />
                  {f.name}
                </label>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Query Editor */}
      <div className="query-editor">
        <div className="query-type-selector">
          <button
            className={queryType === 'sql' ? 'active' : ''}
            onClick={() => setQueryType('sql')}
          >
            SQL
          </button>
          <button
            className={queryType === 'natural_language' ? 'active' : ''}
            onClick={() => setQueryType('natural_language')}
          >
            Natural Language
          </button>
        </div>

        {queryType === 'sql' ? (
          <MonacoEditor
            language="sql"
            value={query}
            onChange={setQuery}
            options={{
              minimap: { enabled: false },
              lineNumbers: 'on',
              // Add autocomplete for context metrics, datasets, columns
            }}
          />
        ) : (
          <textarea
            placeholder="Ask a question about your data..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
          />
        )}

        <button onClick={executeQuery} disabled={loading || !query}>
          {loading ? 'Executing...' : 'Execute Query'}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="query-results">
          <div className="results-metadata">
            <p>Execution time: {results.execution_time_ms}ms</p>
            <p>Rows: {results.result_preview.row_count}</p>
            {results.used_relationships && (
              <p>Used relationships: {results.used_relationships.join(', ')}</p>
            )}
            {results.used_metrics && (
              <p>Used metrics: {results.used_metrics.join(', ')}</p>
            )}
          </div>

          <DataTable data={results.result_preview} />

          {results.generated_query && (
            <div className="generated-sql">
              <h4>Generated SQL:</h4>
              <pre>{results.generated_query}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Example Queries with Context

### Example 1: Simple Multi-Dataset Query
```sql
-- Context: ecommerce_basic
-- User writes simplified query
SELECT customer_name, total_revenue
FROM customers
WHERE customer_status = 'active'
ORDER BY total_revenue DESC
LIMIT 10

-- System expands with context:
-- - total_revenue → SUM(o.order_amount)
-- - Adds JOIN from customer_orders relationship
-- - Result:
SELECT
    c.customer_name,
    SUM(o.order_amount) as total_revenue
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_status = 'active'
GROUP BY c.customer_name
ORDER BY total_revenue DESC
LIMIT 10
```

### Example 2: Natural Language with Context
```
Question: "What is the average order value for each product category last month?"

Context: ecommerce_basic
- Datasets: customers, orders, products
- Relationships: customer_orders, order_products
- Metrics: avg_order_value = AVG(o.order_amount)

Generated SQL:
SELECT
    p.category,
    AVG(o.order_amount) as avg_order_value,
    COUNT(o.order_id) as order_count
FROM orders o
INNER JOIN products p ON o.product_id = p.product_id
WHERE o.order_date >= DATE('now', '-30 days')
GROUP BY p.category
ORDER BY avg_order_value DESC
```

### Example 3: Complex Healthcare Query
```
Question: "Show readmission rates by treatment type for adult patients"

Context: healthcare_outcomes
- Datasets: patients, treatments, outcomes
- Relationships: patient_treatments, treatment_outcomes
- Metrics: readmission_rate
- Filters: adult_patients (age >= 18)

Generated SQL:
SELECT
    tx.treatment_type,
    COUNT(DISTINCT pt.patient_id) as patient_count,
    (SUM(CASE WHEN oc.readmission_days <= 30 THEN 1 ELSE 0 END) * 100.0) /
        COUNT(DISTINCT oc.patient_id) as readmission_rate
FROM patients pt
INNER JOIN treatments tx ON pt.patient_id = tx.patient_id
LEFT JOIN outcomes oc ON tx.treatment_id = oc.treatment_id
WHERE (JULIANDAY('now') - JULIANDAY(pt.date_of_birth)) / 365.25 >= 18
GROUP BY tx.treatment_type
ORDER BY readmission_rate DESC
```

---

## Success Metrics

- Context-aware query adoption rate > 40%
- Natural language accuracy with context > 90%
- Multi-dataset query execution time < 2 seconds
- Reduction in manual JOIN writing by 80%
- User satisfaction with context integration > 4.5/5

---

## Future Enhancements

1. **Visual Query Builder**
   - Drag-and-drop datasets from context
   - Visual relationship mapping
   - Point-and-click metric selection

2. **Context Recommendations**
   - Suggest relevant contexts based on query
   - Auto-create contexts from query patterns
   - Context versioning and evolution

3. **Advanced Features**
   - Parameterized queries using context filters
   - Query templates library
   - Cross-context queries (multiple contexts)

---

## Documentation

- [ ] User guide for context-aware queries
- [ ] Natural language query examples with context
- [ ] Best practices for context design
- [ ] API documentation
- [ ] This feature spec
