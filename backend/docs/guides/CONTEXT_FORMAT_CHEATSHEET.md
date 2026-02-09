# Context Format Cheat Sheet

Quick reference for all supported context formats.

---

## Option 1: Simple Single Dataset

**When to use**: Quick documentation, one dataset, no relationships

```markdown
# Dataset Name

Describe your dataset here. What does it contain?

## Key Fields
- Field 1
- Field 2

## Analysis Ideas
- Question 1
- Question 2
```

**Create with:**
```python
await context_service.create_context(
    user_id=user_id,
    content=markdown,
    dataset_id="your-dataset-uuid"  # Required!
)
```

---

## Option 2: Simple Multi-Dataset (List)

**When to use**: Multiple datasets, basic relationships, plain English

```markdown
# Context Name

Description of your multi-dataset context.

## Datasets

- Dataset1 (id: uuid-1)
- Dataset2 (id: uuid-2)
- Dataset3 (id: uuid-3)

## Relationships

- Dataset1 → Dataset2 via column_name
- Dataset1 → Dataset3 via other_column
```

**Create with:**
```python
await context_service.create_context(
    user_id=user_id,
    content=markdown  # IDs extracted from markdown!
)
```

---

## Option 3: Simple Multi-Dataset (Headers)

**When to use**: Multiple datasets with individual descriptions

```markdown
# Context Name

Overall description.

## Dataset: Orders (id: uuid-1)

Description of orders dataset.

## Dataset: Customers (id: uuid-2)

Description of customers dataset.

## Relationships

- Orders → Customers via customer_id
```

**Create with:**
```python
await context_service.create_context(
    user_id=user_id,
    content=markdown  # IDs extracted from markdown!
)
```

---

## Option 4: Structured (Full YAML)

**When to use**: Need metrics, glossary, filters, full control

```yaml
---
name: "Context Name"
version: "1.0.0"
description: "Full description"
context_type: "multi_dataset"
datasets:
  - id: "orders"
    name: "Orders"
    dataset_id: "uuid-1"
    columns:
      - name: "order_id"
        business_name: "Order ID"
        description: "Unique identifier"
  - id: "customers"
    name: "Customers"
    dataset_id: "uuid-2"
relationships:
  - id: "order_customer"
    from_dataset: "orders"
    from_column: "customer_id"
    to_dataset: "customers"
    to_column: "customer_id"
metrics:
  - id: "total_revenue"
    expression: "SUM(orders.total_amount)"
    name: "Total Revenue"
glossary:
  - term: "Customer Lifetime Value"
    definition: "Total revenue per customer"
filters:
  - id: "vip_only"
    condition: "segment = 'VIP'"
---

# Markdown Content

Detailed documentation here...
```

**Create with:**
```python
await context_service.create_context(
    user_id=user_id,
    content=yaml_and_markdown
)
```

---

## Quick Comparison

| Feature | Option 1 | Option 2 | Option 3 | Option 4 |
|---------|----------|----------|----------|----------|
| **Datasets** | 1 | Multiple | Multiple | Multiple |
| **Relationships** | ❌ | ✅ Basic | ✅ Basic | ✅ Advanced |
| **Metrics** | ❌ | ❌ | ❌ | ✅ |
| **Glossary** | ❌ | ❌ | ❌ | ✅ |
| **Filters** | ❌ | ❌ | ❌ | ✅ |
| **YAML Required** | ❌ | ❌ | ❌ | ✅ |
| **Complexity** | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## Relationship Syntax

Both arrow styles work:

```markdown
## Relationships

- Orders → Customers via customer_id
- Orders -> Products via product_id
```

---

## Dataset ID Syntax

Both styles work:

```markdown
## Datasets

- Orders (id: uuid-here)
- Customers (id: another-uuid)

## Or:

## Dataset: Orders (id: uuid-here)
## Dataset: Customers (id: another-uuid)
```

---

## Auto-Generated Fields

All simple formats auto-generate:

| Field | Value |
|-------|-------|
| version | 1.0.0 |
| status | active |
| context_type | single_dataset or multi_dataset (auto-detected) |
| name | From first `#` header |
| description | From first paragraph (200 chars) |

---

## Examples

### E-Commerce
```markdown
# E-Commerce Analytics

Orders, customers, and products analysis.

## Datasets
- Orders (id: order-uuid)
- Customers (id: customer-uuid)
- Products (id: product-uuid)

## Relationships
- Orders → Customers via customer_id
- Orders → Products via product_id
```

### Amazon Products
```markdown
# Amazon Product Reviews

Products and AI-generated review narratives.

## Datasets
- Products (id: products-uuid)
- Narratives (id: narratives-uuid)

## Relationships
- Narratives → Products via product_id
```

### Sales & Inventory
```markdown
# Sales & Inventory

## Dataset: Sales (id: sales-uuid)
Daily sales transactions.

## Dataset: Inventory (id: inventory-uuid)
Current stock levels.

## Relationships
- Sales → Inventory via product_id
```

---

## Performance

All formats have **identical performance**:

- Context lookup: ~0.7ms (Phase 2 FK)
- Create time: ~20ms
- Auto-population: Works for all

---

## Quick Decision Tree

**Need metrics/glossary/filters?**
- YES → Use Option 4 (Structured YAML)
- NO → Continue

**Multiple datasets?**
- NO → Use Option 1 (Simple Single)
- YES → Continue

**Need relationships?**
- NO → Use Option 2 or 3 (your preference)
- YES → Use Option 2 or 3 (your preference)

**Prefer individual descriptions per dataset?**
- YES → Use Option 3 (Headers)
- NO → Use Option 2 (List)

---

**TL;DR:**
- Simple = No YAML
- Structured = Full YAML
- Both work great!
