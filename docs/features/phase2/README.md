# Phase 2: Context & Multi-Dataset (Weeks 5-8)

## Overview
Advanced features enabling multi-dataset analysis with context-aware queries, automatic relationship resolution, and AI-powered insights.

## Status
📋 **PLANNED** (Starts after Phase 1 completion)

---

## Features

### 🚧 1. Context File Management
**File:** `context-file-management.md`
**Status:** ✅ DOCUMENTED (Ready for Implementation)

Define relationships, metrics, and business rules across multiple datasets.

**Capabilities:**
- YAML frontmatter context definitions
- Dataset relationship management (JOIN definitions)
- Custom metrics (calculated fields)
- Business rules (validation, quality checks)
- Pre-defined filters
- Multi-level validation (schema, semantic, circular dependency)
- Version control for contexts

**Example:**
```yaml
---
name: ecommerce_basic
version: 1.0.0

datasets:
  - id: customers_ds
  - id: orders_ds

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
---
```

---

### 🚧 2. Query Engine (Multi-Dataset Extension)
**File:** `../phase1/02-query-engine.md` (Extended in Phase 2)
**Status:** 🚧 IN PROGRESS

**Phase 2 Focus:** Multi-dataset query capabilities
- Context-aware query execution
- Automatic JOIN generation from relationships
- Custom metric expansion
- Business rule enforcement
- Query optimization and caching
- Query templates

**Components to Implement:**
- `QueryParser` - Parse natural language with context
- `RelationshipResolver` - Find optimal join paths
- `SQLGenerator` - Generate multi-dataset SQL
- `BusinessRulesEngine` - Apply context rules
- `CacheManager` - Redis-based caching

---

### 🚧 3. Visualization (Advanced)
**File:** `../phase1/03-visualization-charts.md` (Extended in Phase 2)
**Status:** 🚧 IN PROGRESS

**Phase 2 Focus:** AI-powered features
- AI chart suggestions (Claude AI)
- Context-aware visualizations
- Multi-dataset chart recommendations
- Advanced chart types (heatmap, box plots)
- Tableau integration (optional)

### 🚧 4. Natural Language Visualization Generation
**File:** `natural-language-visualization.md`
**Status:** ✅ DOCUMENTED (Ready for Implementation)

**NEW FEATURE:** Generate visualizations from plain text descriptions

**Capabilities:**
- Parse natural language to chart configuration
- Automatic chart type selection
- Aggregation function detection
- Column validation with suggestions
- Real-time visualization generation
- "Understanding" feedback to users

**Example:**
```
User types: "show average screen time by age group"
System generates: Bar chart with age_group on x-axis,
                  total_screen_time on y-axis, mean aggregation
```

**Key Benefits:**
- 10x faster than manual configuration
- Lowers barrier for non-technical users
- Natural, conversational interface
- Immediate feedback on interpretation

---

## Implementation Order

1. **Week 5: Context Management Backend**
   - Context model and database schema
   - Context service (CRUD operations)
   - Validation engine
   - Context API routes

2. **Week 6: Context Management Frontend**
   - Context upload interface
   - Context editor (YAML)
   - Context validation display
   - Context list and details pages

3. **Week 7: Multi-Dataset Query Engine**
   - QueryParser with context integration
   - RelationshipResolver (graph algorithms)
   - SQLGenerator for multi-dataset
   - BusinessRulesEngine
   - Query execution with context

4. **Week 8: Advanced Visualization**
   - AI suggestion engine
   - Natural language visualization generation
   - Context-aware viz recommendations
   - Tableau integration
   - Testing and polish

---

## Dependencies

```
Phase 1 Complete:
├── Data Upload (✅)
├── Authentication (✅)
├── Query Engine - Single (✅)
└── Visualization - Basic (✅)
         │
         ▼
Phase 2:
├── Context Management (🚧)
│        ├──→ Multi-Dataset Query Engine (🚧)
│        └──→ Advanced Visualization (🚧)
```

---

## Success Criteria

- [ ] Users can create and manage context files
- [ ] Context validation catches errors (circular deps, missing columns)
- [ ] Multi-dataset queries execute correctly
- [ ] Natural language queries work across datasets
- [ ] AI suggests appropriate visualizations (>85% accuracy)
- [ ] Natural language visualization generation works (>80% parse success)
- [ ] NL viz response time <5 seconds end-to-end
- [ ] Query execution time <2s for 2-3 dataset joins
- [ ] Context-aware query adoption rate >40%
- [ ] NL visualization adoption rate >20% within first week
- [ ] All Phase 2 features have >90% test coverage

---

## Technical Challenges

### 1. Relationship Resolution
**Challenge:** Finding optimal join paths through multiple datasets
**Solution:** Implement graph algorithms (A* or Dijkstra) to find shortest path

### 2. Query Optimization
**Challenge:** Multi-dataset queries can be slow
**Solution:**
- Push down filters early
- Use proper join order
- Implement result caching
- Add database indexes

### 3. Context Validation
**Challenge:** Validating complex context definitions with circular dependencies
**Solution:**
- Multi-phase validation (schema → semantic → circular)
- Graph traversal for cycle detection
- Column existence checks against actual datasets

### 4. Natural Language Understanding
**Challenge:** Translating complex multi-dataset questions to SQL
**Solution:**
- Enhanced LLM prompts with full context schema
- Context examples in prompts
- Query explanation for user verification

---

## Next Phase

See [Phase 3](../phase3/README.md) for dashboard, analytics, and performance optimization.
