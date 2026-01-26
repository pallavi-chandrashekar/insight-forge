# Context File Management Feature

## 1. Overview

### Purpose and Value Proposition

The Context File Management system enables users to define relationships, custom metrics, business rules, and filters across multiple datasets using human-readable Markdown files with YAML frontmatter. This feature is the foundation for multi-dataset analysis in InsightForge, allowing the Query Engine to understand how to join disparate datasets and apply domain-specific logic.

**Key Value Propositions:**
- **Declarative Data Relationships**: Define complex dataset joins without writing SQL
- **Business Logic Centralization**: Store metrics, rules, and filters in version-controllable files
- **Natural Language Query Enhancement**: Context definitions enable AI to generate accurate multi-dataset queries
- **Reusability**: Share and version context definitions across teams
- **Validation & Safety**: Multi-level validation prevents circular dependencies and schema conflicts

### Key Capabilities

1. **Context Definition**: Create Markdown files with YAML frontmatter defining dataset relationships
2. **Multi-Level Validation**:
   - Schema validation (YAML structure)
   - Semantic validation (dataset existence, column references)
   - Circular dependency detection
3. **Relationship Management**: Define inner, left, right, and outer joins between datasets
4. **Custom Metrics**: Create calculated fields using SQL-like expressions
5. **Business Rules**: Define data quality rules and validation constraints
6. **Filters**: Pre-define commonly used filter conditions
7. **Version Control**: Track changes to context definitions over time
8. **Integration**: Seamless integration with Multi-Dataset Query Engine

### User Personas and Use Cases

#### Persona 1: Data Analyst (Sarah)
**Background**: Analyzes sales and customer data daily, needs to join multiple datasets regularly.

**Use Cases**:
- Create a context file defining relationships between customers, orders, and products
- Define custom metrics like "Average Order Value" and "Customer Lifetime Value"
- Save commonly used filters (e.g., "Active Customers Last 90 Days")
- Share context files with team members for consistent analysis

#### Persona 2: Business Intelligence Developer (Mike)
**Background**: Builds data models and maintains business logic centrally.

**Use Cases**:
- Define complex multi-dataset relationships with proper join conditions
- Create reusable business metrics that enforce company-wide definitions
- Implement data quality rules and validation logic
- Version control context files alongside code in Git

#### Persona 3: Healthcare Data Scientist (Dr. Chen)
**Background**: Analyzes patient outcomes across multiple medical systems.

**Use Cases**:
- Link patient demographics, treatments, and outcomes datasets
- Define clinical metrics (e.g., "30-Day Readmission Rate")
- Apply HIPAA-compliant filters (e.g., "Exclude patients under 18")
- Validate data quality rules before analysis

#### Persona 4: Financial Analyst (Jessica)
**Background**: Performs portfolio analysis across accounts, transactions, and market data.

**Use Cases**:
- Define relationships between accounts, transactions, and securities
- Create financial metrics (ROI, Sharpe Ratio, Portfolio Beta)
- Set up date range filters for fiscal periods
- Ensure data consistency across analysis

---

## 2. Context File Format Specification

### Complete YAML Schema

```yaml
---
# Context Metadata (Required)
name: string                    # Unique identifier for this context
version: string                 # Semantic version (e.g., "1.0.0")
description: string             # Human-readable description
created_by: string              # User ID or email
created_at: ISO8601 datetime    # Creation timestamp
updated_at: ISO8601 datetime    # Last update timestamp

# Datasets (Required) - Minimum 1 dataset
datasets:
  - id: string                  # Unique identifier within this context
    name: string                # Display name
    dataset_id: UUID            # Reference to InsightForge dataset ID
    alias: string               # SQL alias for this dataset (optional)
    description: string         # Description (optional)

# Relationships (Optional) - Defines how datasets join
relationships:
  - id: string                  # Unique relationship identifier
    name: string                # Display name
    description: string         # Description (optional)
    left_dataset: string        # ID from datasets array
    right_dataset: string       # ID from datasets array
    join_type: enum             # "inner" | "left" | "right" | "outer"
    conditions:                 # Join conditions (array)
      - left_column: string     # Column name in left dataset
        operator: enum          # "=" | "!=" | ">" | "<" | ">=" | "<="
        right_column: string    # Column name in right dataset
        condition_type: enum    # "on" | "and" | "or" (default: "on")

# Custom Metrics (Optional) - Calculated fields
metrics:
  - id: string                  # Unique metric identifier
    name: string                # Display name
    description: string         # Description (optional)
    expression: string          # SQL-like expression
    data_type: enum             # "integer" | "float" | "string" | "boolean" | "date"
    format: string              # Display format (optional, e.g., "$,.2f")
    datasets: array[string]     # Dataset IDs this metric applies to

# Business Rules (Optional) - Data quality and validation
business_rules:
  - id: string                  # Unique rule identifier
    name: string                # Display name
    description: string         # Description (optional)
    rule_type: enum             # "validation" | "quality" | "constraint"
    condition: string           # SQL-like condition expression
    severity: enum              # "error" | "warning" | "info"
    datasets: array[string]     # Dataset IDs this rule applies to
    error_message: string       # Message when rule fails (optional)

# Filters (Optional) - Pre-defined filter conditions
filters:
  - id: string                  # Unique filter identifier
    name: string                # Display name
    description: string         # Description (optional)
    condition: string           # SQL-like WHERE clause
    datasets: array[string]     # Dataset IDs this filter applies to
    parameters: array           # Optional parameterized filters
      - name: string            # Parameter name
        data_type: enum         # "integer" | "float" | "string" | "date"
        default: any            # Default value (optional)

# Settings (Optional) - Context-level configuration
settings:
  default_join_type: enum       # Default join type if not specified ("inner")
  enable_circular_check: boolean # Enable circular dependency detection (true)
  max_join_depth: integer       # Maximum allowed join depth (10)
  cache_ttl_seconds: integer    # Cache TTL for this context (3600)
---
```

### Field Constraints and Validation Rules

#### Required Fields
- `name`: 3-100 characters, alphanumeric with underscores/hyphens
- `version`: Must follow semantic versioning (e.g., "1.0.0", "2.1.3")
- `description`: 10-500 characters
- `datasets`: Array with at least 1 dataset

#### Relationship Validation
- `left_dataset` and `right_dataset` must reference valid dataset IDs
- `join_type` must be one of: "inner", "left", "right", "outer"
- `operator` must be one of: "=", "!=", ">", "<", ">=", "<="
- Columns referenced must exist in respective datasets
- No circular dependencies allowed (A→B→C→A)

#### Metric Validation
- `expression` must be valid SQL syntax
- Column references must exist in specified datasets
- `data_type` must match expression result type
- Metric IDs must be unique within context

#### Business Rule Validation
- `condition` must be valid SQL boolean expression
- `severity` must be "error", "warning", or "info"
- Referenced columns must exist in specified datasets

#### Filter Validation
- `condition` must be valid SQL WHERE clause syntax
- Parameterized filters must use `{parameter_name}` syntax
- Parameter data types must match usage in condition

### Markdown Structure

Context files use Markdown with YAML frontmatter. The structure is:

```markdown
---
[YAML Frontmatter as defined above]
---

# Context Documentation

## Overview
[Human-readable description of this context]

## Datasets
[Description of each dataset and its role]

## Relationships
[Explanation of how datasets are related]

## Metrics
[Definition and business logic for each metric]

## Business Rules
[Explanation of data quality rules]

## Usage Examples
[Code examples showing how to use this context]

## Change Log
[Version history and changes]
```

### Example Context Files

#### Example 1: E-commerce (Simple)

```yaml
---
name: ecommerce_basic
version: 1.0.0
description: Basic e-commerce context linking customers, orders, and products
created_by: sarah@company.com
created_at: 2026-01-26T10:00:00Z
updated_at: 2026-01-26T10:00:00Z

datasets:
  - id: customers_ds
    name: Customers
    dataset_id: a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d
    alias: c
    description: Customer master data

  - id: orders_ds
    name: Orders
    dataset_id: b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e
    alias: o
    description: Order transactions

  - id: products_ds
    name: Products
    dataset_id: c3d4e5f6-a7b8-4c5d-0e1f-2a3b4c5d6e7f
    alias: p
    description: Product catalog

relationships:
  - id: customer_orders
    name: Customer to Orders
    description: Links customers to their orders
    left_dataset: customers_ds
    right_dataset: orders_ds
    join_type: left
    conditions:
      - left_column: customer_id
        operator: "="
        right_column: customer_id
        condition_type: on

  - id: order_products
    name: Orders to Products
    description: Links orders to products
    left_dataset: orders_ds
    right_dataset: products_ds
    join_type: inner
    conditions:
      - left_column: product_id
        operator: "="
        right_column: product_id
        condition_type: on

metrics:
  - id: total_revenue
    name: Total Revenue
    description: Sum of order amounts
    expression: SUM(o.order_amount)
    data_type: float
    format: "$,.2f"
    datasets: [orders_ds]

  - id: avg_order_value
    name: Average Order Value
    description: Average order amount per customer
    expression: AVG(o.order_amount)
    data_type: float
    format: "$,.2f"
    datasets: [orders_ds]

filters:
  - id: active_customers
    name: Active Customers
    description: Customers who placed orders in last 90 days
    condition: c.last_order_date >= DATE('now', '-90 days')
    datasets: [customers_ds]

settings:
  default_join_type: inner
  enable_circular_check: true
  max_join_depth: 5
  cache_ttl_seconds: 3600
---

# E-commerce Basic Context

## Overview
This context defines the basic relationships between customers, orders, and products for e-commerce analysis.

## Datasets
- **Customers**: Contains customer demographic and contact information
- **Orders**: Transactional order data including amounts and dates
- **Products**: Product catalog with pricing and categories

## Relationships
- Customers → Orders: One-to-many relationship via customer_id
- Orders → Products: Many-to-one relationship via product_id

## Metrics
- **Total Revenue**: Aggregated order amounts
- **Average Order Value**: Mean order value for analysis

## Usage Examples
```sql
-- Get top customers by revenue
SELECT c.customer_name, SUM(o.order_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY total_revenue DESC
LIMIT 10
```
```

#### Example 2: Healthcare (Medium Complexity)

```yaml
---
name: healthcare_outcomes
version: 1.2.0
description: Healthcare context for patient outcomes analysis
created_by: dr.chen@hospital.org
created_at: 2026-01-15T08:30:00Z
updated_at: 2026-01-26T14:20:00Z

datasets:
  - id: patients_ds
    name: Patients
    dataset_id: d4e5f6a7-b8c9-4d5e-1f2a-3b4c5d6e7f8a
    alias: pt
    description: Patient demographics and enrollment data

  - id: treatments_ds
    name: Treatments
    dataset_id: e5f6a7b8-c9d0-4e5f-2a3b-4c5d6e7f8a9b
    alias: tx
    description: Treatment procedures and medications

  - id: outcomes_ds
    name: Outcomes
    dataset_id: f6a7b8c9-d0e1-4f5a-3b4c-5d6e7f8a9b0c
    alias: oc
    description: Patient outcomes and follow-up data

relationships:
  - id: patient_treatments
    name: Patient Treatments
    description: Links patients to their treatment records
    left_dataset: patients_ds
    right_dataset: treatments_ds
    join_type: inner
    conditions:
      - left_column: patient_id
        operator: "="
        right_column: patient_id
        condition_type: on

  - id: treatment_outcomes
    name: Treatment Outcomes
    description: Links treatments to outcome records
    left_dataset: treatments_ds
    right_dataset: outcomes_ds
    join_type: left
    conditions:
      - left_column: treatment_id
        operator: "="
        right_column: treatment_id
        condition_type: on
      - left_column: patient_id
        operator: "="
        right_column: patient_id
        condition_type: and

metrics:
  - id: readmission_rate
    name: 30-Day Readmission Rate
    description: Percentage of patients readmitted within 30 days
    expression: >
      (SUM(CASE WHEN oc.readmission_days <= 30 THEN 1 ELSE 0 END) * 100.0) /
      COUNT(DISTINCT oc.patient_id)
    data_type: float
    format: ".2f%"
    datasets: [outcomes_ds]

  - id: avg_los
    name: Average Length of Stay
    description: Average hospital stay duration in days
    expression: AVG(tx.length_of_stay_days)
    data_type: float
    format: ".1f"
    datasets: [treatments_ds]

  - id: patient_age
    name: Patient Age
    description: Calculated patient age from birthdate
    expression: (JULIANDAY('now') - JULIANDAY(pt.date_of_birth)) / 365.25
    data_type: integer
    datasets: [patients_ds]

business_rules:
  - id: valid_age
    name: Valid Patient Age
    description: Patients must be 18 or older
    rule_type: validation
    condition: (JULIANDAY('now') - JULIANDAY(pt.date_of_birth)) / 365.25 >= 18
    severity: error
    datasets: [patients_ds]
    error_message: Patient must be 18 years or older

  - id: treatment_date_validity
    name: Treatment Date Validity
    description: Treatment date must be after patient enrollment
    rule_type: validation
    condition: tx.treatment_date >= pt.enrollment_date
    severity: error
    datasets: [treatments_ds, patients_ds]
    error_message: Treatment date cannot precede enrollment date

  - id: outcome_completeness
    name: Outcome Data Completeness
    description: Warning if outcome data is missing
    rule_type: quality
    condition: oc.outcome_status IS NOT NULL
    severity: warning
    datasets: [outcomes_ds]
    error_message: Outcome status should be recorded

filters:
  - id: adult_patients
    name: Adult Patients Only
    description: Filters for patients 18 and older
    condition: (JULIANDAY('now') - JULIANDAY(pt.date_of_birth)) / 365.25 >= 18
    datasets: [patients_ds]

  - id: recent_treatments
    name: Recent Treatments
    description: Treatments in the last N days
    condition: tx.treatment_date >= DATE('now', '-{days} days')
    datasets: [treatments_ds]
    parameters:
      - name: days
        data_type: integer
        default: 90

  - id: high_risk_outcomes
    name: High Risk Outcomes
    description: Patients with readmission or complications
    condition: oc.readmission_days <= 30 OR oc.complications = true
    datasets: [outcomes_ds]

settings:
  default_join_type: inner
  enable_circular_check: true
  max_join_depth: 10
  cache_ttl_seconds: 1800
---

# Healthcare Outcomes Analysis Context

## Overview
This context supports clinical outcomes analysis by linking patient demographics, treatments, and follow-up outcomes. It includes HIPAA-compliant filters and clinical quality metrics.

## Datasets
- **Patients**: De-identified patient demographics, enrollment dates, and basic health information
- **Treatments**: Inpatient and outpatient treatment records including procedures and medications
- **Outcomes**: Follow-up data including readmissions, complications, and recovery status

## Relationships
- Patients → Treatments: One-to-many (one patient can have multiple treatments)
- Treatments → Outcomes: One-to-one or one-to-many (tracks follow-up outcomes)

## Metrics
- **30-Day Readmission Rate**: Key quality metric for hospital performance
- **Average Length of Stay**: Resource utilization metric
- **Patient Age**: Calculated field for age-based analysis

## Business Rules
- Age validation ensures only adult patients (18+) are analyzed
- Treatment dates must be logically consistent with enrollment
- Outcome completeness warnings help identify data quality issues

## Usage Examples
```sql
-- Calculate readmission rate by treatment type
SELECT
  tx.treatment_type,
  COUNT(DISTINCT pt.patient_id) as patient_count,
  (SUM(CASE WHEN oc.readmission_days <= 30 THEN 1 ELSE 0 END) * 100.0) /
    COUNT(DISTINCT oc.patient_id) as readmission_rate
FROM patients pt
JOIN treatments tx ON pt.patient_id = tx.patient_id
LEFT JOIN outcomes oc ON tx.treatment_id = oc.treatment_id
WHERE (JULIANDAY('now') - JULIANDAY(pt.date_of_birth)) / 365.25 >= 18
GROUP BY tx.treatment_type
```

## Change Log
- v1.2.0 (2026-01-26): Added high-risk outcomes filter and outcome completeness rule
- v1.1.0 (2026-01-20): Added parameterized recent treatments filter
- v1.0.0 (2026-01-15): Initial release
```

#### Example 3: Finance (Complex)

```yaml
---
name: portfolio_analysis
version: 2.0.1
description: Financial portfolio analysis with accounts, transactions, and market data
created_by: jessica@investment.com
created_at: 2025-12-01T09:00:00Z
updated_at: 2026-01-26T16:45:00Z

datasets:
  - id: accounts_ds
    name: Accounts
    dataset_id: a7b8c9d0-e1f2-4a5b-3c4d-5e6f7a8b9c0d
    alias: acc
    description: Investment account master data

  - id: transactions_ds
    name: Transactions
    dataset_id: b8c9d0e1-f2a3-4b5c-4d5e-6f7a8b9c0d1e
    alias: txn
    description: Buy, sell, and dividend transactions

  - id: securities_ds
    name: Securities
    dataset_id: c9d0e1f2-a3b4-4c5d-5e6f-7a8b9c0d1e2f
    alias: sec
    description: Security master data and pricing

  - id: market_data_ds
    name: Market Data
    dataset_id: d0e1f2a3-b4c5-4d5e-6f7a-8b9c0d1e2f3a
    alias: mkt
    description: Historical market prices and indices

relationships:
  - id: account_transactions
    name: Account Transactions
    description: Links accounts to their transactions
    left_dataset: accounts_ds
    right_dataset: transactions_ds
    join_type: left
    conditions:
      - left_column: account_id
        operator: "="
        right_column: account_id
        condition_type: on

  - id: transaction_securities
    name: Transaction Securities
    description: Links transactions to securities
    left_dataset: transactions_ds
    right_dataset: securities_ds
    join_type: inner
    conditions:
      - left_column: security_id
        operator: "="
        right_column: security_id
        condition_type: on

  - id: security_market_data
    name: Security Market Data
    description: Links securities to market pricing
    left_dataset: securities_ds
    right_dataset: market_data_ds
    join_type: left
    conditions:
      - left_column: security_id
        operator: "="
        right_column: security_id
        condition_type: on
      - left_column: price_date
        operator: "="
        right_column: market_date
        condition_type: and

metrics:
  - id: portfolio_value
    name: Portfolio Value
    description: Current market value of all holdings
    expression: SUM(txn.shares * mkt.current_price)
    data_type: float
    format: "$,.2f"
    datasets: [transactions_ds, market_data_ds]

  - id: roi_percent
    name: Return on Investment
    description: Percentage return on investment
    expression: >
      ((mkt.current_price - txn.cost_basis) / txn.cost_basis) * 100
    data_type: float
    format: ".2f%"
    datasets: [transactions_ds, market_data_ds]

  - id: portfolio_beta
    name: Portfolio Beta
    description: Weighted portfolio beta
    expression: >
      SUM(
        (txn.shares * mkt.current_price * sec.beta) /
        SUM(txn.shares * mkt.current_price)
      )
    data_type: float
    format: ".3f"
    datasets: [transactions_ds, securities_ds, market_data_ds]

  - id: dividend_yield
    name: Dividend Yield
    description: Annual dividend yield percentage
    expression: (sec.annual_dividend / mkt.current_price) * 100
    data_type: float
    format: ".2f%"
    datasets: [securities_ds, market_data_ds]

  - id: account_age_years
    name: Account Age (Years)
    description: Years since account opening
    expression: (JULIANDAY('now') - JULIANDAY(acc.open_date)) / 365.25
    data_type: float
    format: ".1f"
    datasets: [accounts_ds]

business_rules:
  - id: valid_transaction_amount
    name: Valid Transaction Amount
    description: Transaction amount must be positive
    rule_type: validation
    condition: txn.transaction_amount > 0
    severity: error
    datasets: [transactions_ds]
    error_message: Transaction amount must be greater than zero

  - id: valid_shares
    name: Valid Share Quantity
    description: Share quantity must be positive for buy transactions
    rule_type: validation
    condition: >
      txn.transaction_type != 'BUY' OR
      (txn.transaction_type = 'BUY' AND txn.shares > 0)
    severity: error
    datasets: [transactions_ds]
    error_message: Buy transactions must have positive share quantity

  - id: transaction_date_order
    name: Transaction Date Order
    description: Transaction date must be after account opening
    rule_type: validation
    condition: txn.transaction_date >= acc.open_date
    severity: error
    datasets: [transactions_ds, accounts_ds]
    error_message: Transaction date cannot precede account opening

  - id: price_freshness
    name: Market Price Freshness
    description: Market prices should be recent (within 2 days)
    rule_type: quality
    condition: JULIANDAY('now') - JULIANDAY(mkt.market_date) <= 2
    severity: warning
    datasets: [market_data_ds]
    error_message: Market price data may be stale

  - id: concentrated_position
    name: Concentrated Position Warning
    description: Warn if single security exceeds 20% of portfolio
    rule_type: quality
    condition: >
      (txn.shares * mkt.current_price) /
      SUM(txn.shares * mkt.current_price) <= 0.20
    severity: warning
    datasets: [transactions_ds, market_data_ds]
    error_message: Position exceeds 20% concentration threshold

filters:
  - id: active_accounts
    name: Active Accounts
    description: Accounts with active status
    condition: acc.account_status = 'ACTIVE'
    datasets: [accounts_ds]

  - id: date_range
    name: Date Range
    description: Filter transactions by date range
    condition: >
      txn.transaction_date >= '{start_date}' AND
      txn.transaction_date <= '{end_date}'
    datasets: [transactions_ds]
    parameters:
      - name: start_date
        data_type: date
        default: 2025-01-01
      - name: end_date
        data_type: date
        default: 2025-12-31

  - id: equity_securities
    name: Equity Securities Only
    description: Filter for equity securities (stocks)
    condition: sec.security_type = 'EQUITY'
    datasets: [securities_ds]

  - id: high_value_accounts
    name: High Value Accounts
    description: Accounts with balance above threshold
    condition: acc.current_balance >= {min_balance}
    datasets: [accounts_ds]
    parameters:
      - name: min_balance
        data_type: float
        default: 100000.0

  - id: profitable_positions
    name: Profitable Positions
    description: Positions with positive returns
    condition: mkt.current_price > txn.cost_basis
    datasets: [transactions_ds, market_data_ds]

settings:
  default_join_type: inner
  enable_circular_check: true
  max_join_depth: 15
  cache_ttl_seconds: 600
---

# Portfolio Analysis Context

## Overview
This context supports comprehensive portfolio analysis across accounts, transactions, securities, and market data. It includes financial metrics, risk indicators, and compliance rules.

## Datasets
- **Accounts**: Investment account information including account types, owners, and balances
- **Transactions**: Historical buy, sell, and dividend transactions with cost basis tracking
- **Securities**: Master data for stocks, bonds, funds including ticker symbols and characteristics
- **Market Data**: Real-time and historical pricing data for valuation

## Relationships
Complex four-way relationship structure:
- Accounts → Transactions: Track all activity per account
- Transactions → Securities: Link trades to specific securities
- Securities → Market Data: Current and historical pricing
- Complete chain: Accounts → Transactions → Securities → Market Data

## Metrics
- **Portfolio Value**: Total market value across all holdings
- **ROI**: Return on investment for individual positions
- **Portfolio Beta**: Risk measure relative to market
- **Dividend Yield**: Income generation metric
- **Account Age**: For understanding account maturity

## Business Rules
- **Validation Rules**: Ensure data integrity (positive amounts, valid dates)
- **Quality Rules**: Data freshness warnings and concentration risk alerts
- **Compliance**: Transaction ordering and position size monitoring

## Usage Examples
```sql
-- Calculate portfolio performance by account
SELECT
  acc.account_number,
  acc.account_name,
  SUM(txn.shares * mkt.current_price) as current_value,
  SUM(txn.shares * txn.cost_basis) as cost_basis,
  ((SUM(txn.shares * mkt.current_price) - SUM(txn.shares * txn.cost_basis)) /
    SUM(txn.shares * txn.cost_basis)) * 100 as roi_percent
FROM accounts acc
JOIN transactions txn ON acc.account_id = txn.account_id
JOIN securities sec ON txn.security_id = sec.security_id
JOIN market_data mkt ON sec.security_id = mkt.security_id
  AND mkt.market_date = (SELECT MAX(market_date) FROM market_data)
WHERE acc.account_status = 'ACTIVE'
GROUP BY acc.account_number, acc.account_name
ORDER BY roi_percent DESC
```

## Change Log
- v2.0.1 (2026-01-26): Added concentrated position warning rule
- v2.0.0 (2026-01-15): Added market data dataset and portfolio beta metric
- v1.5.0 (2025-12-20): Added parameterized filters for date ranges and balances
- v1.0.0 (2025-12-01): Initial release with basic account-transaction analysis
```

---

## 3. API Endpoints

### 3.1 Create Context

**Endpoint**: `POST /api/contexts`

**Description**: Creates a new context from a Markdown file or JSON payload.

**Authentication**: Required (JWT)

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data  OR  application/json
```

**Request Body (File Upload)**:
```
{
  "file": <binary file data>,
  "validate_datasets": true,  // Optional, default true
  "auto_version": true         // Optional, auto-increment version if name exists
}
```

**Request Body (JSON)**:
```json
{
  "name": "ecommerce_basic",
  "version": "1.0.0",
  "description": "Basic e-commerce context",
  "content": "---\nname: ecommerce_basic\n...",  // Full markdown content
  "validate_datasets": true,
  "auto_version": false
}
```

**Response (Success - 201 Created)**:
```json
{
  "status": "success",
  "data": {
    "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "name": "ecommerce_basic",
    "version": "1.0.0",
    "created_at": "2026-01-26T10:00:00Z",
    "validation_status": "passed",
    "datasets_count": 3,
    "relationships_count": 2,
    "metrics_count": 2,
    "url": "/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c"
  }
}
```

**Response (Validation Error - 422 Unprocessable Entity)**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Context validation failed",
    "details": {
      "schema_errors": [
        {
          "field": "datasets[0].dataset_id",
          "error": "Dataset 'a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d' not found"
        }
      ],
      "semantic_errors": [
        {
          "field": "relationships[0].conditions[0].left_column",
          "error": "Column 'customer_id' does not exist in dataset 'customers_ds'"
        }
      ],
      "circular_dependencies": []
    }
  }
}
```

**Error Codes**:
- `400`: Bad Request - Invalid file format or JSON
- `401`: Unauthorized - Missing or invalid token
- `409`: Conflict - Context with same name and version exists
- `422`: Unprocessable Entity - Validation errors
- `500`: Internal Server Error

**Example curl**:
```bash
# Upload file
curl -X POST https://api.insightforge.com/api/contexts \
  -H "Authorization: Bearer eyJhbGc..." \
  -F "file=@ecommerce_context.md" \
  -F "validate_datasets=true"

# JSON payload
curl -X POST https://api.insightforge.com/api/contexts \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ecommerce_basic",
    "version": "1.0.0",
    "description": "Basic e-commerce context",
    "content": "---\nname: ecommerce_basic\nversion: 1.0.0\n..."
  }'
```

### 3.2 Get Context

**Endpoint**: `GET /api/contexts/{context_id}`

**Description**: Retrieves a context by ID with full parsed structure.

**Authentication**: Required (JWT)

**Path Parameters**:
- `context_id` (UUID): Context identifier

**Query Parameters**:
- `include_markdown` (boolean): Include raw markdown content (default: false)
- `resolve_datasets` (boolean): Include full dataset schemas (default: true)

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "name": "ecommerce_basic",
    "version": "1.0.0",
    "description": "Basic e-commerce context",
    "created_by": "sarah@company.com",
    "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "created_at": "2026-01-26T10:00:00Z",
    "updated_at": "2026-01-26T10:00:00Z",
    "datasets": [
      {
        "id": "customers_ds",
        "name": "Customers",
        "dataset_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
        "alias": "c",
        "description": "Customer master data",
        "schema": {
          "columns": [
            {"name": "customer_id", "type": "integer"},
            {"name": "customer_name", "type": "string"},
            {"name": "email", "type": "string"}
          ]
        }
      }
    ],
    "relationships": [
      {
        "id": "customer_orders",
        "name": "Customer to Orders",
        "description": "Links customers to their orders",
        "left_dataset": "customers_ds",
        "right_dataset": "orders_ds",
        "join_type": "left",
        "conditions": [
          {
            "left_column": "customer_id",
            "operator": "=",
            "right_column": "customer_id",
            "condition_type": "on"
          }
        ]
      }
    ],
    "metrics": [...],
    "business_rules": [...],
    "filters": [...],
    "settings": {...},
    "markdown_content": "...",  // If include_markdown=true
    "validation_status": "passed",
    "cache_info": {
      "cached_at": "2026-01-26T10:00:00Z",
      "expires_at": "2026-01-26T11:00:00Z"
    }
  }
}
```

**Error Codes**:
- `401`: Unauthorized
- `403`: Forbidden - Context belongs to another user
- `404`: Not Found - Context doesn't exist
- `500`: Internal Server Error

**Example curl**:
```bash
curl -X GET https://api.insightforge.com/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c \
  -H "Authorization: Bearer eyJhbGc..." \
  -G -d "include_markdown=true" -d "resolve_datasets=true"
```

### 3.3 List Contexts

**Endpoint**: `GET /api/contexts`

**Description**: Lists all contexts for the authenticated user.

**Authentication**: Required (JWT)

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20, max: 100)
- `sort_by` (string): Sort field - "name", "created_at", "updated_at" (default: "updated_at")
- `sort_order` (string): "asc" or "desc" (default: "desc")
- `search` (string): Search in name and description
- `version` (string): Filter by version

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "contexts": [
      {
        "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
        "name": "ecommerce_basic",
        "version": "1.0.0",
        "description": "Basic e-commerce context",
        "created_at": "2026-01-26T10:00:00Z",
        "updated_at": "2026-01-26T10:00:00Z",
        "datasets_count": 3,
        "relationships_count": 2,
        "metrics_count": 2
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 45,
      "total_pages": 3
    }
  }
}
```

**Example curl**:
```bash
curl -X GET https://api.insightforge.com/api/contexts \
  -H "Authorization: Bearer eyJhbGc..." \
  -G -d "page=1" -d "page_size=20" -d "search=ecommerce"
```

### 3.4 Update Context

**Endpoint**: `PUT /api/contexts/{context_id}`

**Description**: Updates an existing context.

**Authentication**: Required (JWT)

**Path Parameters**:
- `context_id` (UUID): Context identifier

**Request Body**:
```json
{
  "content": "---\nname: ecommerce_basic\nversion: 1.1.0\n...",
  "validate_datasets": true,
  "increment_version": true  // Auto-increment version number
}
```

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "context_id": "f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c",
    "name": "ecommerce_basic",
    "version": "1.1.0",
    "updated_at": "2026-01-26T11:00:00Z",
    "changes": {
      "added_metrics": ["customer_lifetime_value"],
      "modified_relationships": [],
      "removed_filters": []
    }
  }
}
```

**Error Codes**:
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden - Cannot modify another user's context
- `404`: Not Found
- `422`: Validation errors
- `500`: Internal Server Error

**Example curl**:
```bash
curl -X PUT https://api.insightforge.com/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "...",
    "increment_version": true
  }'
```

### 3.5 Delete Context

**Endpoint**: `DELETE /api/contexts/{context_id}`

**Description**: Deletes a context.

**Authentication**: Required (JWT)

**Path Parameters**:
- `context_id` (UUID): Context identifier

**Query Parameters**:
- `force` (boolean): Force delete even if used in queries (default: false)

**Response (Success - 204 No Content)**:
```
(Empty response body)
```

**Response (Conflict - 409)**:
```json
{
  "status": "error",
  "error": {
    "code": "CONTEXT_IN_USE",
    "message": "Context is referenced by existing queries",
    "details": {
      "query_count": 5,
      "queries": [
        {"query_id": "...", "name": "Top Customers Report"}
      ]
    }
  }
}
```

**Example curl**:
```bash
curl -X DELETE https://api.insightforge.com/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c \
  -H "Authorization: Bearer eyJhbGc..."
```

### 3.6 Validate Context

**Endpoint**: `POST /api/contexts/validate`

**Description**: Validates a context without saving it.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "content": "---\nname: test_context\n...",
  "validation_level": "full"  // "schema" | "semantic" | "full"
}
```

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "valid": true,
    "validation_level": "full",
    "schema_validation": {
      "passed": true,
      "errors": []
    },
    "semantic_validation": {
      "passed": true,
      "errors": [],
      "warnings": []
    },
    "circular_dependency_check": {
      "passed": true,
      "circular_paths": []
    }
  }
}
```

**Response (Validation Failed - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "valid": false,
    "validation_level": "full",
    "schema_validation": {
      "passed": false,
      "errors": [
        {
          "field": "datasets",
          "message": "At least one dataset is required",
          "severity": "error"
        }
      ]
    },
    "semantic_validation": {
      "passed": false,
      "errors": [
        {
          "field": "relationships[0].left_dataset",
          "message": "Dataset 'unknown_ds' not found in datasets array",
          "severity": "error"
        }
      ],
      "warnings": [
        {
          "field": "metrics[0].expression",
          "message": "Column 'revenue' not found in specified datasets",
          "severity": "warning"
        }
      ]
    },
    "circular_dependency_check": {
      "passed": true,
      "circular_paths": []
    }
  }
}
```

**Example curl**:
```bash
curl -X POST https://api.insightforge.com/api/contexts/validate \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "---\nname: test\nversion: 1.0.0\n...",
    "validation_level": "full"
  }'
```

### 3.7 Get Relationships

**Endpoint**: `GET /api/contexts/{context_id}/relationships`

**Description**: Get all relationships defined in a context (used by Query Engine).

**Authentication**: Required (JWT)

**Path Parameters**:
- `context_id` (UUID): Context identifier

**Query Parameters**:
- `resolve_columns` (boolean): Include column information (default: true)

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "relationships": [
      {
        "id": "customer_orders",
        "name": "Customer to Orders",
        "left_dataset": {
          "id": "customers_ds",
          "dataset_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
          "alias": "c"
        },
        "right_dataset": {
          "id": "orders_ds",
          "dataset_id": "b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e",
          "alias": "o"
        },
        "join_type": "left",
        "conditions": [
          {
            "left_column": "customer_id",
            "left_column_type": "integer",
            "operator": "=",
            "right_column": "customer_id",
            "right_column_type": "integer",
            "condition_type": "on"
          }
        ],
        "sql_template": "LEFT JOIN orders o ON c.customer_id = o.customer_id"
      }
    ]
  }
}
```

**Example curl**:
```bash
curl -X GET https://api.insightforge.com/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c/relationships \
  -H "Authorization: Bearer eyJhbGc..."
```

### 3.8 Get Metrics

**Endpoint**: `GET /api/contexts/{context_id}/metrics`

**Description**: Get all custom metrics defined in a context (used by Query Engine).

**Authentication**: Required (JWT)

**Path Parameters**:
- `context_id` (UUID): Context identifier

**Query Parameters**:
- `dataset_id` (string): Filter metrics by dataset (optional)

**Response (Success - 200 OK)**:
```json
{
  "status": "success",
  "data": {
    "metrics": [
      {
        "id": "total_revenue",
        "name": "Total Revenue",
        "description": "Sum of order amounts",
        "expression": "SUM(o.order_amount)",
        "data_type": "float",
        "format": "$,.2f",
        "datasets": ["orders_ds"],
        "dependencies": ["order_amount"]
      }
    ]
  }
}
```

**Example curl**:
```bash
curl -X GET https://api.insightforge.com/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c/metrics \
  -H "Authorization: Bearer eyJhbGc..."
```

### 3.9 Export Context

**Endpoint**: `GET /api/contexts/{context_id}/export`

**Description**: Export context as Markdown file.

**Authentication**: Required (JWT)

**Path Parameters**:
- `context_id` (UUID): Context identifier

**Query Parameters**:
- `format` (string): "markdown" or "yaml" (default: "markdown")

**Response (Success - 200 OK)**:
```
Content-Type: text/markdown
Content-Disposition: attachment; filename="ecommerce_basic_v1.0.0.md"

---
name: ecommerce_basic
version: 1.0.0
...
```

**Example curl**:
```bash
curl -X GET https://api.insightforge.com/api/contexts/f1a2b3c4-d5e6-4f5a-6b7c-8d9e0f1a2b3c/export \
  -H "Authorization: Bearer eyJhbGc..." \
  -o ecommerce_context.md
```

---

## 4. Database Schema

### 4.1 SQLAlchemy Models

#### Context Model

```python
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Context(Base):
    """Context file metadata and content"""
    __tablename__ = "contexts"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Context metadata
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    created_by_email = Column(String(255), nullable=True)

    # Content storage
    markdown_content = Column(Text, nullable=False)  # Full markdown file
    parsed_yaml = Column(JSONB, nullable=False)       # Parsed YAML frontmatter

    # Cached parsed structures for performance
    datasets = Column(JSONB, nullable=False)          # Array of dataset definitions
    relationships = Column(JSONB, nullable=True)      # Array of relationships
    metrics = Column(JSONB, nullable=True)            # Array of metrics
    business_rules = Column(JSONB, nullable=True)     # Array of business rules
    filters = Column(JSONB, nullable=True)            # Array of filters
    settings = Column(JSONB, nullable=True)           # Context settings

    # Validation status
    validation_status = Column(String(20), nullable=False, default="pending")  # pending/passed/failed
    validation_errors = Column(JSONB, nullable=True)  # Validation error details

    # Metadata
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 for deduplication

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="contexts")
    query_contexts = relationship("QueryContext", back_populates="context", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index("idx_context_name_version", "name", "version"),
        Index("idx_context_user_name", "user_id", "name"),
        Index("idx_context_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Context {self.name} v{self.version}>"
```

#### QueryContext Association Model

```python
class QueryContext(Base):
    """Association between queries and contexts"""
    __tablename__ = "query_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), nullable=False, index=True)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Track which parts of the context were used
    used_relationships = Column(JSONB, nullable=True)  # Array of relationship IDs used
    used_metrics = Column(JSONB, nullable=True)        # Array of metric IDs used
    used_filters = Column(JSONB, nullable=True)        # Array of filter IDs used

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    query = relationship("Query", back_populates="query_contexts")
    context = relationship("Context", back_populates="query_contexts")

    __table_args__ = (
        Index("idx_query_context_query", "query_id"),
        Index("idx_query_context_context", "context_id"),
    )

    def __repr__(self):
        return f"<QueryContext query={self.query_id} context={self.context_id}>"
```

#### Updated Query Model

```python
# Add to existing Query model in app/models/query.py

class Query(Base):
    __tablename__ = "queries"

    # ... existing fields ...

    # New field for context support
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    query_contexts = relationship("QueryContext", back_populates="query", cascade="all, delete-orphan")
```

#### Updated User Model

```python
# Add to existing User model in app/models/user.py

class User(Base):
    __tablename__ = "users"

    # ... existing fields ...

    # Relationships
    contexts = relationship("Context", back_populates="user", cascade="all, delete-orphan")
```

### 4.2 Database Indexes

**Performance Indexes**:
```sql
-- Context lookup by name and version
CREATE INDEX idx_context_name_version ON contexts (name, version);

-- User's contexts lookup
CREATE INDEX idx_context_user_name ON contexts (user_id, name);

-- Recent contexts
CREATE INDEX idx_context_created_at ON contexts (created_at DESC);

-- File hash for deduplication
CREATE INDEX idx_context_file_hash ON contexts (file_hash);

-- Validation status filtering
CREATE INDEX idx_context_validation_status ON contexts (validation_status);

-- Query-Context associations
CREATE INDEX idx_query_context_query ON query_contexts (query_id);
CREATE INDEX idx_query_context_context ON query_contexts (context_id);
```

**Full-Text Search Index** (PostgreSQL):
```sql
-- Full-text search on name and description
CREATE INDEX idx_context_fts ON contexts
USING gin(to_tsvector('english', name || ' ' || description));
```

### 4.3 Migration Strategy

#### Initial Migration (Alembic)

```python
"""add context file management

Revision ID: 001_add_contexts
Revises: previous_revision
Create Date: 2026-01-26 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_contexts'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Create contexts table
    op.create_table(
        'contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('created_by_email', sa.String(255), nullable=True),
        sa.Column('markdown_content', sa.Text, nullable=False),
        sa.Column('parsed_yaml', postgresql.JSONB, nullable=False),
        sa.Column('datasets', postgresql.JSONB, nullable=False),
        sa.Column('relationships', postgresql.JSONB, nullable=True),
        sa.Column('metrics', postgresql.JSONB, nullable=True),
        sa.Column('business_rules', postgresql.JSONB, nullable=True),
        sa.Column('filters', postgresql.JSONB, nullable=True),
        sa.Column('settings', postgresql.JSONB, nullable=True),
        sa.Column('validation_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('validation_errors', postgresql.JSONB, nullable=True),
        sa.Column('file_size_bytes', sa.Integer, nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('idx_context_user_name', 'contexts', ['user_id', 'name'])
    op.create_index('idx_context_name_version', 'contexts', ['name', 'version'])
    op.create_index('idx_context_created_at', 'contexts', ['created_at'])
    op.create_index('idx_context_file_hash', 'contexts', ['file_hash'])
    op.create_index('idx_context_validation_status', 'contexts', ['validation_status'])

    # Create query_contexts association table
    op.create_table(
        'query_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('query_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('context_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('used_relationships', postgresql.JSONB, nullable=True),
        sa.Column('used_metrics', postgresql.JSONB, nullable=True),
        sa.Column('used_filters', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['query_id'], ['queries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['context_id'], ['contexts.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_query_context_query', 'query_contexts', ['query_id'])
    op.create_index('idx_query_context_context', 'query_contexts', ['context_id'])

    # Add context_id to queries table
    op.add_column('queries', sa.Column('context_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_queries_context', 'queries', 'contexts', ['context_id'], ['id'], ondelete='SET NULL')
    op.create_index('idx_queries_context', 'queries', ['context_id'])

def downgrade():
    # Drop indexes and constraints
    op.drop_index('idx_queries_context', 'queries')
    op.drop_constraint('fk_queries_context', 'queries')
    op.drop_column('queries', 'context_id')

    op.drop_index('idx_query_context_context', 'query_contexts')
    op.drop_index('idx_query_context_query', 'query_contexts')
    op.drop_table('query_contexts')

    op.drop_index('idx_context_validation_status', 'contexts')
    op.drop_index('idx_context_file_hash', 'contexts')
    op.drop_index('idx_context_created_at', 'contexts')
    op.drop_index('idx_context_name_version', 'contexts')
    op.drop_index('idx_context_user_name', 'contexts')
    op.drop_table('contexts')
```

#### Run Migration

```bash
# Generate migration
alembic revision --autogenerate -m "add context file management"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## 5. Service Architecture

### 5.1 ContextService

**File**: `backend/app/services/context_service.py`

```python
import hashlib
import yaml
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from uuid import UUID

from app.models.context import Context, QueryContext
from app.models.dataset import Dataset
from app.services.context_parser import ContextParser
from app.services.validation_engine import ValidationEngine
from app.core.exceptions import (
    ContextNotFoundError,
    ContextValidationError,
    ContextConflictError,
    DatasetNotFoundError
)

class ContextService:
    """Service for managing context files"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = ContextParser()
        self.validator = ValidationEngine(db)

    async def create_context(
        self,
        user_id: UUID,
        markdown_content: str,
        validate_datasets: bool = True,
        auto_version: bool = False
    ) -> Context:
        """
        Create a new context from markdown content.

        Args:
            user_id: User creating the context
            markdown_content: Full markdown file content
            validate_datasets: Whether to validate dataset references
            auto_version: Auto-increment version if name exists

        Returns:
            Created Context object

        Raises:
            ContextValidationError: If validation fails
            ContextConflictError: If context with same name/version exists
        """
        # Parse markdown
        parsed_data = self.parser.parse_markdown(markdown_content)

        # Check for conflicts
        if not auto_version:
            existing = await self._get_by_name_version(
                user_id, parsed_data['name'], parsed_data['version']
            )
            if existing:
                raise ContextConflictError(
                    f"Context '{parsed_data['name']}' version '{parsed_data['version']}' already exists"
                )
        else:
            # Auto-increment version
            parsed_data['version'] = await self._next_version(user_id, parsed_data['name'])

        # Validate
        validation_result = await self.validator.validate(
            parsed_data,
            validate_datasets=validate_datasets,
            user_id=user_id
        )

        if not validation_result.is_valid():
            raise ContextValidationError(
                "Context validation failed",
                validation_result.to_dict()
            )

        # Calculate file hash
        file_hash = hashlib.sha256(markdown_content.encode()).hexdigest()

        # Create context
        context = Context(
            user_id=user_id,
            name=parsed_data['name'],
            version=parsed_data['version'],
            description=parsed_data['description'],
            created_by_email=parsed_data.get('created_by'),
            markdown_content=markdown_content,
            parsed_yaml=parsed_data,
            datasets=parsed_data.get('datasets', []),
            relationships=parsed_data.get('relationships', []),
            metrics=parsed_data.get('metrics', []),
            business_rules=parsed_data.get('business_rules', []),
            filters=parsed_data.get('filters', []),
            settings=parsed_data.get('settings', {}),
            validation_status='passed',
            validation_errors=None,
            file_size_bytes=len(markdown_content.encode()),
            file_hash=file_hash
        )

        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)

        return context

    async def get_context(
        self,
        context_id: UUID,
        user_id: UUID,
        resolve_datasets: bool = True
    ) -> Dict[str, Any]:
        """
        Get context by ID with full parsed structure.

        Args:
            context_id: Context UUID
            user_id: User requesting the context
            resolve_datasets: Whether to include full dataset schemas

        Returns:
            Dictionary with context data

        Raises:
            ContextNotFoundError: If context doesn't exist or user lacks access
        """
        stmt = select(Context).where(
            and_(Context.id == context_id, Context.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        context = result.scalar_one_or_none()

        if not context:
            raise ContextNotFoundError(f"Context {context_id} not found")

        # Build response
        data = {
            'context_id': str(context.id),
            'name': context.name,
            'version': context.version,
            'description': context.description,
            'created_by': context.created_by_email,
            'user_id': str(context.user_id),
            'created_at': context.created_at.isoformat(),
            'updated_at': context.updated_at.isoformat() if context.updated_at else None,
            'datasets': context.datasets,
            'relationships': context.relationships,
            'metrics': context.metrics,
            'business_rules': context.business_rules,
            'filters': context.filters,
            'settings': context.settings,
            'validation_status': context.validation_status
        }

        # Resolve dataset schemas if requested
        if resolve_datasets and context.datasets:
            data['datasets'] = await self._resolve_dataset_schemas(
                context.datasets, user_id
            )

        return data

    async def list_contexts(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'updated_at',
        sort_order: str = 'desc',
        search: Optional[str] = None,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List contexts for a user with pagination.

        Args:
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Sort field
            sort_order: 'asc' or 'desc'
            search: Search query for name/description
            version: Filter by version

        Returns:
            Dictionary with contexts and pagination info
        """
        # Build query
        stmt = select(Context).where(Context.user_id == user_id)

        # Apply filters
        if search:
            stmt = stmt.where(
                or_(
                    Context.name.ilike(f'%{search}%'),
                    Context.description.ilike(f'%{search}%')
                )
            )

        if version:
            stmt = stmt.where(Context.version == version)

        # Apply sorting
        if sort_order == 'desc':
            stmt = stmt.order_by(getattr(Context, sort_by).desc())
        else:
            stmt = stmt.order_by(getattr(Context, sort_by).asc())

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = await self.db.scalar(count_stmt)

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute
        result = await self.db.execute(stmt)
        contexts = result.scalars().all()

        # Format response
        return {
            'contexts': [
                {
                    'context_id': str(c.id),
                    'name': c.name,
                    'version': c.version,
                    'description': c.description,
                    'created_at': c.created_at.isoformat(),
                    'updated_at': c.updated_at.isoformat() if c.updated_at else None,
                    'datasets_count': len(c.datasets) if c.datasets else 0,
                    'relationships_count': len(c.relationships) if c.relationships else 0,
                    'metrics_count': len(c.metrics) if c.metrics else 0
                }
                for c in contexts
            ],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_items': total_items,
                'total_pages': (total_items + page_size - 1) // page_size
            }
        }

    async def update_context(
        self,
        context_id: UUID,
        user_id: UUID,
        markdown_content: str,
        validate_datasets: bool = True,
        increment_version: bool = False
    ) -> Context:
        """Update an existing context"""
        # Get existing context
        stmt = select(Context).where(
            and_(Context.id == context_id, Context.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        context = result.scalar_one_or_none()

        if not context:
            raise ContextNotFoundError(f"Context {context_id} not found")

        # Parse new content
        parsed_data = self.parser.parse_markdown(markdown_content)

        # Auto-increment version if requested
        if increment_version:
            parsed_data['version'] = self._increment_version(context.version)

        # Validate
        validation_result = await self.validator.validate(
            parsed_data,
            validate_datasets=validate_datasets,
            user_id=user_id
        )

        if not validation_result.is_valid():
            raise ContextValidationError(
                "Context validation failed",
                validation_result.to_dict()
            )

        # Update context
        context.name = parsed_data['name']
        context.version = parsed_data['version']
        context.description = parsed_data['description']
        context.markdown_content = markdown_content
        context.parsed_yaml = parsed_data
        context.datasets = parsed_data.get('datasets', [])
        context.relationships = parsed_data.get('relationships', [])
        context.metrics = parsed_data.get('metrics', [])
        context.business_rules = parsed_data.get('business_rules', [])
        context.filters = parsed_data.get('filters', [])
        context.settings = parsed_data.get('settings', {})
        context.file_hash = hashlib.sha256(markdown_content.encode()).hexdigest()
        context.file_size_bytes = len(markdown_content.encode())

        await self.db.commit()
        await self.db.refresh(context)

        return context

    async def delete_context(
        self,
        context_id: UUID,
        user_id: UUID,
        force: bool = False
    ) -> None:
        """Delete a context"""
        # Get context
        stmt = select(Context).where(
            and_(Context.id == context_id, Context.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        context = result.scalar_one_or_none()

        if not context:
            raise ContextNotFoundError(f"Context {context_id} not found")

        # Check if context is in use
        if not force:
            usage_count = await self._check_context_usage(context_id)
            if usage_count > 0:
                raise ContextConflictError(
                    f"Context is referenced by {usage_count} queries. Use force=true to delete anyway."
                )

        await self.db.delete(context)
        await self.db.commit()

    async def get_relationships(
        self,
        context_id: UUID,
        user_id: UUID,
        resolve_columns: bool = True
    ) -> List[Dict[str, Any]]:
        """Get relationships for Query Engine integration"""
        context = await self.get_context(context_id, user_id, resolve_datasets=resolve_columns)
        relationships = context.get('relationships', [])

        if resolve_columns:
            # Add column type information
            datasets_map = {ds['id']: ds for ds in context.get('datasets', [])}

            for rel in relationships:
                left_ds = datasets_map.get(rel['left_dataset'])
                right_ds = datasets_map.get(rel['right_dataset'])

                for condition in rel['conditions']:
                    # Add column types
                    if left_ds:
                        left_col = next(
                            (c for c in left_ds.get('schema', {}).get('columns', [])
                             if c['name'] == condition['left_column']),
                            None
                        )
                        if left_col:
                            condition['left_column_type'] = left_col['type']

                    if right_ds:
                        right_col = next(
                            (c for c in right_ds.get('schema', {}).get('columns', [])
                             if c['name'] == condition['right_column']),
                            None
                        )
                        if right_col:
                            condition['right_column_type'] = right_col['type']

                # Generate SQL template
                rel['sql_template'] = self._generate_join_sql(rel, left_ds, right_ds)

        return relationships

    async def get_metrics(
        self,
        context_id: UUID,
        user_id: UUID,
        dataset_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics for Query Engine integration"""
        context = await self.get_context(context_id, user_id, resolve_datasets=False)
        metrics = context.get('metrics', [])

        # Filter by dataset if specified
        if dataset_id:
            metrics = [
                m for m in metrics
                if dataset_id in m.get('datasets', [])
            ]

        return metrics

    # Helper methods

    async def _get_by_name_version(
        self,
        user_id: UUID,
        name: str,
        version: str
    ) -> Optional[Context]:
        """Get context by name and version"""
        stmt = select(Context).where(
            and_(
                Context.user_id == user_id,
                Context.name == name,
                Context.version == version
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _next_version(self, user_id: UUID, name: str) -> str:
        """Get next version number for a context name"""
        stmt = select(Context.version).where(
            and_(Context.user_id == user_id, Context.name == name)
        ).order_by(Context.version.desc())
        result = await self.db.execute(stmt)
        latest_version = result.scalar_one_or_none()

        if not latest_version:
            return "1.0.0"

        return self._increment_version(latest_version)

    def _increment_version(self, version: str) -> str:
        """Increment semantic version"""
        parts = version.split('.')
        if len(parts) != 3:
            return "1.0.0"

        major, minor, patch = map(int, parts)
        patch += 1
        return f"{major}.{minor}.{patch}"

    async def _resolve_dataset_schemas(
        self,
        datasets: List[Dict[str, Any]],
        user_id: UUID
    ) -> List[Dict[str, Any]]:
        """Resolve full dataset schemas"""
        resolved = []

        for ds in datasets:
            dataset_id = ds.get('dataset_id')
            if dataset_id:
                # Fetch dataset from database
                stmt = select(Dataset).where(
                    and_(
                        Dataset.id == UUID(dataset_id),
                        Dataset.user_id == user_id
                    )
                )
                result = await self.db.execute(stmt)
                dataset = result.scalar_one_or_none()

                if dataset:
                    ds['schema'] = dataset.schema
                    ds['row_count'] = dataset.row_count
                    ds['column_count'] = dataset.column_count

            resolved.append(ds)

        return resolved

    async def _check_context_usage(self, context_id: UUID) -> int:
        """Check how many queries use this context"""
        stmt = select(func.count()).select_from(QueryContext).where(
            QueryContext.context_id == context_id
        )
        return await self.db.scalar(stmt)

    def _generate_join_sql(
        self,
        relationship: Dict[str, Any],
        left_ds: Dict[str, Any],
        right_ds: Dict[str, Any]
    ) -> str:
        """Generate SQL JOIN template from relationship"""
        join_type = relationship['join_type'].upper()
        right_alias = right_ds.get('alias', right_ds['name'])
        left_alias = left_ds.get('alias', left_ds['name'])

        conditions = []
        for cond in relationship['conditions']:
            left_col = f"{left_alias}.{cond['left_column']}"
            right_col = f"{right_alias}.{cond['right_column']}"
            op = cond['operator']
            conditions.append(f"{left_col} {op} {right_col}")

        conditions_str = f" {relationship['conditions'][0].get('condition_type', 'AND').upper()} ".join(conditions)

        return f"{join_type} JOIN {right_ds['name']} {right_alias} ON {conditions_str}"
```

This is part 1 of the document. I'll continue with the remaining sections in the next response.