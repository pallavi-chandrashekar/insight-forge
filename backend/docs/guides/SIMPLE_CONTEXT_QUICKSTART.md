# Simple Context Format - Quick Start

## ✨ What Changed?

You can now create contexts with **plain markdown** - no YAML required!

---

## Before (Structured Format)

```yaml
---
name: "Sales Data"
version: "1.0.0"
description: "Monthly sales"
datasets:
  - id: "sales"
    name: "Sales"
    dataset_id: "abc-123"
---

# Sales Data
Monthly sales information...
```

**Issues:**
- Need to learn YAML syntax
- Complex structure
- Easy to make syntax errors
- Intimidating for non-technical users

---

## After (Simple Format) ✨

```markdown
# Sales Data

Monthly sales information for all products and regions.

## What's Included
- Product sales by month
- Regional breakdowns
- Customer segments

## Key Questions
- What are the top selling products?
- Which region has highest revenue?
```

**Benefits:**
- ✅ Just write markdown
- ✅ No YAML knowledge needed
- ✅ Faster to create
- ✅ Perfect for basic documentation

---

## How to Use

### 1. Write Markdown

```markdown
# Your Dataset Name

Describe your dataset here. What does it contain?

## Key Information
- Important field 1
- Important field 2

## Analysis Ideas
- Question 1
- Question 2
```

### 2. Create Context (API)

```python
await context_service.create_context(
    user_id=user_id,
    content=your_markdown,
    dataset_id=dataset_id  # Required!
)
```

### 3. Done!

The system automatically:
- Extracts name from first header
- Creates description from content
- Links to your dataset
- Sets sensible defaults

---

## What Gets Auto-Generated?

| Field | Value |
|-------|-------|
| **name** | First `#` header |
| **version** | `1.0.0` |
| **description** | First paragraph (200 chars) |
| **context_type** | `single_dataset` |
| **status** | `active` |
| **datasets** | Your dataset_id |

---

## Example: Your Amazon Dataset

```markdown
# About Dataset
📦 Amazon Reviews & AI Narratives Dataset

## 📖 Overview
This dataset contains structured information for ~5,000 Amazon products enriched with AI-generated review narratives. It combines product metadata (category, pricing, ratings, links) with natural language summaries generated using large language models (LLMs).

The dataset is suitable for NLP research, data science projects, recommendation systems, product analytics, and machine learning experimentation.

## 📂 Files Included

### final_narratives.csv
- Product name and categories
- Ratings and number of reviews
- Pricing information
- Product links
- AI-generated narratives

### complete_results.csv
- Raw model generations
- Intermediate pipeline fields
- Additional metadata

## 🧠 Potential Use Cases
- Natural Language Processing (summarization, text quality evaluation)
- Product review analysis
- Recommender systems
- Sentiment analysis
- E-commerce analytics
```

**Create with:**
```python
await context_service.create_context(
    user_id=user_id,
    content=markdown_above,
    dataset_id="your-dataset-uuid"
)
```

---

## Two Formats, One System

Both formats work together:

| Feature | Simple | Structured |
|---------|--------|------------|
| Markdown Description | ✅ | ✅ |
| Pre-defined Metrics | ❌ | ✅ |
| Business Glossary | ❌ | ✅ |
| Custom Filters | ❌ | ✅ |
| Multi-Dataset | ❌ | ✅ |
| Easy to Write | ✅ | ❌ |
| Phase 2 FK Speed | ✅ | ✅ |

**Rule of Thumb:**
- **Simple**: Quick documentation, single dataset, no special features
- **Structured**: Advanced features, metrics, glossary, multi-dataset

---

## Test It

```bash
cd backend
python test_simple_context.py
```

**Expected:**
```
✅ Simple format works (plain markdown)
✅ Structured format works (YAML + markdown)
✅ Backward compatibility maintained
```

---

## Summary

🎉 **Context creation just got easier!**

- ✅ No YAML required (unless you want advanced features)
- ✅ Just write natural markdown
- ✅ Auto-generates structure
- ✅ Same performance as structured format
- ✅ Backward compatible

**Try it out with your Amazon dataset!**
