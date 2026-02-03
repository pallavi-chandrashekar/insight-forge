# Updated Context File Management Specification

## Overview

Context files in InsightForge serve as **comprehensive documentation and metadata** for datasets. They can be created for:
1. **Single datasets** - Rich documentation for one dataset
2. **Multi-dataset relationships** - Define how datasets relate and work together

Context files are human-readable Markdown files with YAML frontmatter that serve as:
- **Data Dictionary**: Column-level documentation and business definitions
- **Data Catalog**: Searchable metadata and business context
- **Data Model**: Entity relationships and schema documentation
- **Query Library**: Sample queries and common use cases
- **Data Quality Rules**: Validation rules and quality metrics
- **Business Logic**: Custom metrics and calculations

---

## Key Value Propositions

### For Single-Dataset Contexts:
- **Self-Documenting Data**: Rich metadata makes data self-explanatory
- **Business Glossary**: Map technical columns to business terms
- **Data Quality**: Define and track quality metrics
- **Onboarding**: New team members quickly understand data
- **Governance**: Track data lineage, ownership, and compliance

### For Multi-Dataset Contexts:
- **Relationship Management**: Define how datasets connect
- **Cross-Dataset Analysis**: Enable complex multi-dataset queries
- **Consistent Metrics**: Ensure everyone calculates metrics the same way
- **Natural Language Queries**: AI uses context to generate accurate SQL

---

## Complete YAML Schema

```yaml
---
# ============================================================
# METADATA (Required)
# ============================================================
name: string                    # Unique identifier (e.g., "sales_data_context")
version: string                 # Semantic version (e.g., "1.0.0")
description: string             # Human-readable description
context_type: enum              # "single_dataset" | "multi_dataset"
created_by: string              # User ID or email
created_at: ISO8601 datetime    # Creation timestamp
updated_at: ISO8601 datetime    # Last update timestamp

# Optional metadata
tags: array[string]             # Tags for categorization (e.g., ["sales", "finance"])
category: string                # Business category (e.g., "Revenue Analytics")
owner: string                   # Data owner/steward
status: enum                    # "draft" | "active" | "deprecated"

# ============================================================
# DATASETS (Required) - Minimum 1 dataset
# ============================================================
datasets:
  - id: string                  # Unique identifier within this context
    name: string                # Display name
    dataset_id: UUID            # Reference to InsightForge dataset ID
    alias: string               # SQL alias (optional, for multi-dataset)
    description: string         # Business description

    # SINGLE-DATASET: Rich metadata
    domain: string              # Business domain (e.g., "Customer Data", "Transactions")
    source_system: string       # Origin system (e.g., "Salesforce", "PostgreSQL")
    refresh_frequency: string   # How often updated (e.g., "daily", "real-time")
    data_owner: string          # Person responsible
    data_steward: string        # Technical contact

    # Data catalog information
    catalog:
      business_name: string     # Business-friendly name
      purpose: string           # Why this data exists
      usage_notes: string       # How to use this data
      limitations: string       # Known limitations or caveats
      compliance: array[string] # Compliance tags (e.g., ["PII", "GDPR", "HIPAA"])
      data_lineage: string      # Where data comes from

    # Column-level documentation (Data Dictionary)
    columns:
      - name: string            # Column name
        business_name: string   # Business-friendly name
        description: string     # What this column represents
        data_type: string       # Data type (e.g., "integer", "varchar")
        nullable: boolean       # Can be null?
        primary_key: boolean    # Is primary key?
        foreign_key: string     # References table.column
        example_values: array   # Sample values
        valid_values: array     # Allowed values (for enums)
        tags: array[string]     # Tags (e.g., ["PII", "sensitive"])
        calculation: string     # How it's calculated (if derived)
        business_rules: string  # Business rules governing this column

    # Sample queries for this dataset
    sample_queries:
      - name: string            # Query name
        description: string     # What it does
        query: string           # SQL query
        use_case: string        # When to use it

    # Data quality metrics
    quality_metrics:
      - metric: string          # Metric name (e.g., "completeness")
        target: float           # Target value (e.g., 0.95)
        current: float          # Current value
        last_checked: datetime  # When last measured

# ============================================================
# RELATIONSHIPS (Optional) - For multi-dataset contexts
# ============================================================
relationships:
  - id: string                  # Unique relationship identifier
    name: string                # Display name
    description: string         # Description
    left_dataset: string        # ID from datasets array
    right_dataset: string       # ID from datasets array
    join_type: enum             # "inner" | "left" | "right" | "outer"
    cardinality: enum           # "one-to-one" | "one-to-many" | "many-to-many"
    conditions:                 # Join conditions
      - left_column: string     # Column in left dataset
        operator: enum          # "=" | "!=" | ">" | "<" | ">=" | "<="
        right_column: string    # Column in right dataset
        condition_type: enum    # "on" | "and" | "or"

# ============================================================
# DATA MODEL & ER DIAGRAM (Optional)
# ============================================================
data_model:
  # Entity definitions
  entities:
    - name: string              # Entity name
      type: enum                # "fact" | "dimension" | "bridge"
      description: string       # Business description
      primary_key: array[string] # Primary key columns
      attributes: array[string]  # Non-key columns

  # ER Diagram (Mermaid syntax for visualization)
  er_diagram: |
    erDiagram
        CUSTOMER ||--o{ ORDER : places
        ORDER ||--|{ LINE_ITEM : contains
        PRODUCT ||--o{ LINE_ITEM : "ordered in"
        CUSTOMER {
            int customer_id PK
            string name
            string email
        }
        ORDER {
            int order_id PK
            int customer_id FK
            date order_date
        }

# ============================================================
# CUSTOM METRICS (Optional)
# ============================================================
metrics:
  - id: string                  # Unique metric identifier
    name: string                # Display name
    description: string         # What it measures
    expression: string          # SQL expression
    data_type: enum             # "integer" | "float" | "string" | "date"
    format: string              # Display format (e.g., "$,.2f")
    datasets: array[string]     # Applicable datasets
    category: string            # Metric category (e.g., "Revenue", "Growth")
    owner: string               # Who maintains this metric

# ============================================================
# BUSINESS RULES (Optional)
# ============================================================
business_rules:
  - id: string                  # Rule identifier
    name: string                # Display name
    description: string         # What it enforces
    rule_type: enum             # "validation" | "quality" | "constraint"
    condition: string           # SQL condition
    severity: enum              # "error" | "warning" | "info"
    datasets: array[string]     # Applicable datasets
    error_message: string       # Message when rule fails

# ============================================================
# FILTERS & SEGMENTS (Optional)
# ============================================================
filters:
  - id: string                  # Filter identifier
    name: string                # Display name
    description: string         # What it filters
    condition: string           # SQL WHERE clause
    datasets: array[string]     # Applicable datasets
    parameters:                 # Parameterized filters
      - name: string            # Parameter name
        data_type: enum         # Data type
        default: any            # Default value

# ============================================================
# GLOSSARY (Optional) - Business term definitions
# ============================================================
glossary:
  - term: string                # Business term
    definition: string          # Definition
    synonyms: array[string]     # Alternative names
    related_columns: array[string] # Mapped columns
    examples: string            # Usage examples

# ============================================================
# SETTINGS (Optional)
# ============================================================
settings:
  default_join_type: enum       # "inner" | "left" | "right" | "outer"
  enable_circular_check: boolean
  max_join_depth: integer
  cache_ttl_seconds: integer
---
```

---

## Example 1: Single-Dataset Context (Sales Data)

```yaml
---
name: sales_data_comprehensive
version: 1.0.0
description: Comprehensive context for monthly sales data
context_type: single_dataset
created_by: sarah@company.com
created_at: 2026-01-30T10:00:00Z
updated_at: 2026-01-30T10:00:00Z
tags: ["sales", "revenue", "analytics"]
category: "Revenue Analytics"
owner: "Sarah Johnson"
status: "active"

datasets:
  - id: sales_monthly
    name: "Monthly Sales Data"
    dataset_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    alias: "sales"
    description: "Monthly aggregated sales data by product and region"

    domain: "Sales & Revenue"
    source_system: "Salesforce"
    refresh_frequency: "daily at 2am UTC"
    data_owner: "Sarah Johnson (sarah@company.com)"
    data_steward: "Mike Chen (mike@company.com)"

    catalog:
      business_name: "Sales Performance Data"
      purpose: "Track monthly sales performance across products and regions for executive reporting and forecasting"
      usage_notes: "Use this dataset for monthly/quarterly reporting. For real-time sales, use the daily_transactions dataset"
      limitations: "Data is aggregated to month-level. Individual transactions not available. Returns/refunds are netted out."
      compliance: ["Financial Data", "Public"]
      data_lineage: "Salesforce → ETL Pipeline → Data Warehouse → InsightForge"

    columns:
      - name: "month"
        business_name: "Sales Month"
        description: "First day of the month for which sales are aggregated"
        data_type: "date"
        nullable: false
        primary_key: true
        example_values: ["2026-01-01", "2026-02-01"]
        tags: ["time", "required"]
        business_rules: "Always the first day of the month"

      - name: "region"
        business_name: "Sales Region"
        description: "Geographic region where sale occurred"
        data_type: "string"
        nullable: false
        primary_key: true
        valid_values: ["North America", "Europe", "Asia Pacific", "Latin America"]
        example_values: ["North America", "Europe"]
        tags: ["geography", "required"]

      - name: "product_category"
        business_name: "Product Category"
        description: "High-level product categorization"
        data_type: "string"
        nullable: false
        primary_key: true
        valid_values: ["Electronics", "Furniture", "Office Supplies"]
        example_values: ["Electronics"]
        tags: ["product", "required"]

      - name: "revenue"
        business_name: "Gross Revenue"
        description: "Total revenue before discounts and returns"
        data_type: "decimal(15,2)"
        nullable: false
        example_values: ["125000.50", "89750.25"]
        tags: ["financial", "metric"]
        calculation: "SUM(order_amount) - SUM(returns_amount)"
        business_rules: "Must be >= 0. Negative values indicate data quality issue."

      - name: "units_sold"
        business_name: "Units Sold"
        description: "Number of units sold in the period"
        data_type: "integer"
        nullable: false
        example_values: ["1250", "897"]
        tags: ["quantity", "metric"]

      - name: "customer_count"
        business_name: "Unique Customers"
        description: "Count of distinct customers who made purchases"
        data_type: "integer"
        nullable: false
        example_values: ["450", "623"]
        tags: ["customer", "metric"]
        calculation: "COUNT(DISTINCT customer_id)"

      - name: "avg_order_value"
        business_name: "Average Order Value"
        description: "Average revenue per order"
        data_type: "decimal(10,2)"
        nullable: true
        example_values: ["250.50", "189.75"]
        tags: ["financial", "calculated"]
        calculation: "revenue / order_count"

    sample_queries:
      - name: "Top Regions by Revenue"
        description: "Find top performing regions in current year"
        use_case: "Monthly executive reporting"
        query: |
          SELECT
            region,
            SUM(revenue) as total_revenue,
            SUM(units_sold) as total_units
          FROM sales_monthly
          WHERE YEAR(month) = YEAR(CURRENT_DATE)
          GROUP BY region
          ORDER BY total_revenue DESC

      - name: "Year-over-Year Growth"
        description: "Calculate YoY revenue growth by category"
        use_case: "Trend analysis and forecasting"
        query: |
          SELECT
            product_category,
            YEAR(month) as year,
            SUM(revenue) as yearly_revenue,
            (SUM(revenue) - LAG(SUM(revenue)) OVER (PARTITION BY product_category ORDER BY YEAR(month))) /
              LAG(SUM(revenue)) OVER (PARTITION BY product_category ORDER BY YEAR(month)) * 100 as yoy_growth_pct
          FROM sales_monthly
          GROUP BY product_category, YEAR(month)

    quality_metrics:
      - metric: "completeness"
        target: 1.0
        current: 0.98
        last_checked: "2026-01-30T08:00:00Z"
      - metric: "revenue_accuracy"
        target: 1.0
        current: 0.995
        last_checked: "2026-01-30T08:00:00Z"

metrics:
  - id: "total_revenue"
    name: "Total Revenue"
    description: "Sum of all revenue across periods"
    expression: "SUM(revenue)"
    data_type: "float"
    format: "$,.2f"
    datasets: ["sales_monthly"]
    category: "Revenue"
    owner: "Finance Team"

  - id: "revenue_per_customer"
    name: "Revenue Per Customer"
    description: "Average revenue per unique customer"
    expression: "SUM(revenue) / SUM(customer_count)"
    data_type: "float"
    format: "$,.2f"
    datasets: ["sales_monthly"]
    category: "Customer Metrics"
    owner: "Sales Team"

business_rules:
  - id: "positive_revenue"
    name: "Revenue Must Be Positive"
    description: "Revenue cannot be negative"
    rule_type: "validation"
    condition: "revenue >= 0"
    severity: "error"
    datasets: ["sales_monthly"]
    error_message: "Negative revenue detected - check for data quality issues"

  - id: "customer_count_check"
    name: "Customer Count Validation"
    description: "If there's revenue, there must be customers"
    rule_type: "quality"
    condition: "revenue = 0 OR customer_count > 0"
    severity: "warning"
    datasets: ["sales_monthly"]
    error_message: "Revenue exists but no customers recorded"

filters:
  - id: "current_year"
    name: "Current Year Only"
    description: "Filter to current calendar year"
    condition: "YEAR(month) = YEAR(CURRENT_DATE)"
    datasets: ["sales_monthly"]

  - id: "high_revenue_months"
    name: "High Revenue Months"
    description: "Months with revenue above threshold"
    condition: "revenue >= {min_revenue}"
    datasets: ["sales_monthly"]
    parameters:
      - name: "min_revenue"
        data_type: "float"
        default: 100000.0

glossary:
  - term: "Revenue"
    definition: "Total monetary value of sales before any deductions"
    synonyms: ["Sales", "Gross Sales", "Top Line"]
    related_columns: ["revenue"]
    examples: "Q1 revenue was $5M. Revenue grew 15% YoY."

  - term: "Average Order Value (AOV)"
    definition: "Mean revenue per customer order"
    synonyms: ["AOV", "Order Value", "Basket Size"]
    related_columns: ["avg_order_value"]
    examples: "Our AOV increased from $150 to $175 this quarter."
---

# Sales Data Context

## Overview
This context file documents the monthly sales dataset used for executive reporting, forecasting, and trend analysis.

## Data Quality
- **Completeness**: 98% (target: 100%)
- **Accuracy**: 99.5% (verified against Salesforce monthly)
- **Timeliness**: Updated daily at 2am UTC

## Common Use Cases
1. **Monthly Revenue Reporting**: Track revenue by region and product
2. **Year-over-Year Comparisons**: Analyze growth trends
3. **Forecasting**: Use historical data for predictions
4. **Executive Dashboards**: Power C-level visualizations

## Known Issues
- Returns are netted out in the same month (not tracked separately)
- Customer count may be slightly inflated due to deduplication logic

## Change Log
- v1.0.0 (2026-01-30): Initial context creation
```

---

## Example 2: Multi-Dataset Context (E-commerce)

```yaml
---
name: ecommerce_complete
version: 1.2.0
description: Complete e-commerce data model with customers, orders, and products
context_type: multi_dataset
created_by: mike@company.com
created_at: 2026-01-20T10:00:00Z
updated_at: 2026-01-30T14:00:00Z
tags: ["ecommerce", "transactions", "customers"]
category: "E-commerce Analytics"
owner: "Mike Chen"
status: "active"

datasets:
  - id: customers_ds
    name: "Customers"
    dataset_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    alias: "c"
    description: "Customer master data with demographics and registration info"
    domain: "Customer Data"
    source_system: "CRM Database"

  - id: orders_ds
    name: "Orders"
    dataset_id: "b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e"
    alias: "o"
    description: "Transactional order data"
    domain: "Transaction Data"
    source_system: "E-commerce Platform"

  - id: products_ds
    name: "Products"
    dataset_id: "c3d4e5f6-a7b8-4c5d-0e1f-2a3b4c5d6e7f"
    alias: "p"
    description: "Product catalog with pricing"
    domain: "Product Data"
    source_system: "Product Database"

relationships:
  - id: customer_orders
    name: "Customer to Orders"
    description: "Links customers to their purchase history"
    left_dataset: customers_ds
    right_dataset: orders_ds
    join_type: left
    cardinality: "one-to-many"
    conditions:
      - left_column: customer_id
        operator: "="
        right_column: customer_id
        condition_type: on

  - id: order_products
    name: "Orders to Products"
    description: "Links orders to purchased products"
    left_dataset: orders_ds
    right_dataset: products_ds
    join_type: inner
    cardinality: "many-to-one"
    conditions:
      - left_column: product_id
        operator: "="
        right_column: product_id
        condition_type: on

data_model:
  entities:
    - name: "Customer"
      type: "dimension"
      description: "Customer demographic and account information"
      primary_key: ["customer_id"]
      attributes: ["customer_name", "email", "registration_date", "customer_tier"]

    - name: "Order"
      type: "fact"
      description: "Individual customer orders"
      primary_key: ["order_id"]
      attributes: ["order_date", "order_amount", "status"]

    - name: "Product"
      type: "dimension"
      description: "Product catalog information"
      primary_key: ["product_id"]
      attributes: ["product_name", "category", "price", "in_stock"]

  er_diagram: |
    erDiagram
        CUSTOMER ||--o{ ORDER : "places"
        ORDER }o--|| PRODUCT : "contains"
        CUSTOMER {
            int customer_id PK
            string customer_name
            string email
            date registration_date
            string customer_tier
        }
        ORDER {
            int order_id PK
            int customer_id FK
            int product_id FK
            date order_date
            decimal order_amount
        }
        PRODUCT {
            int product_id PK
            string product_name
            string category
            decimal price
        }

metrics:
  - id: "total_revenue"
    name: "Total Revenue"
    description: "Sum of all order amounts"
    expression: "SUM(o.order_amount)"
    data_type: "float"
    format: "$,.2f"
    datasets: ["orders_ds"]
    category: "Revenue"

  - id: "customer_lifetime_value"
    name: "Customer Lifetime Value"
    description: "Total revenue per customer"
    expression: "SUM(o.order_amount)"
    data_type: "float"
    format: "$,.2f"
    datasets: ["customers_ds", "orders_ds"]
    category: "Customer Metrics"

business_rules:
  - id: "order_amount_positive"
    name: "Order Amount Validation"
    description: "Order amounts must be positive"
    rule_type: "validation"
    condition: "o.order_amount > 0"
    severity: "error"
    datasets: ["orders_ds"]
    error_message: "Invalid order amount detected"

glossary:
  - term: "Customer Lifetime Value"
    definition: "Total revenue generated by a customer over their entire relationship"
    synonyms: ["CLV", "LTV", "Lifetime Value"]
    related_columns: ["order_amount"]
    examples: "High CLV customers should receive premium support"
---

# E-commerce Complete Context

## Overview
This context defines the complete e-commerce data model linking customers, orders, and products.

## Entity Relationships
- **Customers** can place multiple **Orders** (one-to-many)
- Each **Order** is for one **Product** (many-to-one)

## Common Queries
See sample_queries in each dataset section.
```

---

## Implementation Notes

### Database Storage
- Store both YAML frontmatter (parsed as JSONB) and full markdown content
- Index on `context_type`, `tags`, `category` for fast filtering
- Support full-text search on description, glossary terms, and markdown content

### Validation Levels
1. **Schema Validation**: YAML structure correctness
2. **Semantic Validation**: Dataset references, column existence
3. **Circular Dependency Detection**: For multi-dataset relationships
4. **Business Rule Validation**: SQL syntax checking

### Frontend Features
- **Context Type Selector**: Single-dataset vs Multi-dataset
- **YAML Editor**: Syntax highlighting and auto-complete
- **ER Diagram Renderer**: Visual display of Mermaid diagrams
- **Data Catalog View**: Searchable column dictionary
- **Glossary Browser**: Business term lookup

This updated specification supports both simple single-dataset documentation and complex multi-dataset relationship definitions.
