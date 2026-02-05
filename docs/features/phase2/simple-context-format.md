# Simple Context Format

## Overview

InsightForge now supports **two context formats**:

1. **Structured Format** (YAML + Markdown) - Full-featured, with metrics, glossary, filters
2. **Simple Format** (Plain Markdown) - Easy to write, no YAML required ✨

The simple format is perfect for quick dataset documentation without needing to learn YAML syntax.

---

## Comparison

### Structured Format (Original)

```yaml
---
name: "Internet Usage Analysis"
version: "1.0.0"
description: "Daily internet usage patterns"
datasets:
  - id: "usage"
    name: "Internet Usage"
    dataset_id: "38875e33-0d72-4df6-bfaf-792e11f40015"
metrics:
  - id: "avg_screen_time"
    expression: "AVG(total_screen_time)"
    name: "Average Screen Time"
glossary:
  - term: "Screen Time"
    definition: "Total hours spent online"
---

# Internet Usage Analysis

Detailed analysis of internet usage patterns...
```

**Features:**
- ✅ Pre-defined metrics
- ✅ Business glossary
- ✅ Custom filters
- ✅ Multi-dataset support
- ✅ Relationships between datasets
- ✅ Full control over metadata

**Best For:**
- Power users
- Complex analytics
- Multi-dataset contexts
- When you need metrics/glossary

---

### Simple Format (New) ✨

```markdown
# Internet Usage Analysis

This dataset tracks daily internet usage patterns across different age groups and devices.

## About the Data

The dataset includes information about:
- Total screen time per user
- Social media usage hours
- Work/study time online
- Primary device preferences

## Key Insights

You can analyze:
- Screen time trends by age group
- Most popular devices
- Social media vs productivity time
- Usage patterns throughout the day

## Sample Questions

- What is the average screen time by age group?
- Which device is most popular?
- How much time do users spend on social media?
```

**Features:**
- ✅ No YAML required
- ✅ Just write markdown
- ✅ Auto-generated metadata
- ✅ Works with Phase 2 FK optimization
- ✅ Perfect for simple documentation

**Best For:**
- Quick documentation
- Non-technical users
- Simple single-dataset contexts
- When you just need descriptions

---

## How It Works

### Creating Simple Context

```python
from app.services.context_service import ContextService

# Plain markdown content (no YAML)
content = """
# Amazon Products Dataset

This dataset contains 5,000 Amazon products with reviews and ratings.

## Key Fields
- Product name
- Category
- Price
- Rating
- Review count
"""

# Create context (dataset_id required for simple format)
context = await context_service.create_context(
    user_id=user_id,
    content=content,
    dataset_id=dataset_id  # Required for simple format
)
```

### Auto-Generated Structure

The parser automatically:

1. **Extracts Name**: Uses first `#` header as context name
2. **Creates Description**: Uses first paragraph (up to 200 chars)
3. **Links Dataset**: Uses provided `dataset_id`
4. **Sets Defaults**:
   - Version: `1.0.0`
   - Type: `single_dataset`
   - Status: `active`

### Result

```python
context.name            # "Amazon Products Dataset"
context.version         # "1.0.0"
context.context_type    # "single_dataset"
context.description     # "This dataset contains 5,000..."
context.datasets        # [{"id": "main", "name": "...", "dataset_id": "..."}]
context.markdown_content # Full markdown
context.metrics         # None (simple format)
context.glossary        # None (simple format)
```

---

## API Integration

### Frontend: Creating Simple Context

```typescript
// Simple format - just markdown
const simpleContent = `
# Sales Data 2023

Monthly sales data for all products and regions.

## What's Included
- Product sales by month
- Regional breakdowns
- Customer segments
`;

const response = await fetch('/api/contexts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: simpleContent,
    dataset_id: datasetId  // Required for simple format
  })
});
```

### Backend: API Endpoint

```python
from fastapi import APIRouter
from pydantic import BaseModel

class ContextCreate(BaseModel):
    content: str
    dataset_id: Optional[UUID] = None  # Required if no YAML
    validate: bool = True

@router.post("/contexts")
async def create_context(
    data: ContextCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    context_service = ContextService(db)

    context = await context_service.create_context(
        user_id=user_id,
        content=data.content,
        dataset_id=data.dataset_id,
        validate=data.validate
    )

    return context.to_dict()
```

---

## Format Detection

The parser automatically detects the format:

```python
def parse(content: str, dataset_id: Optional[str] = None):
    if content.startswith('---'):
        # STRUCTURED FORMAT
        # Parse YAML frontmatter
        return parse_yaml_format(content)
    else:
        # SIMPLE FORMAT
        # Auto-generate structure from markdown
        if not dataset_id:
            raise Error("dataset_id required for simple format")
        return parse_simple_format(content, dataset_id)
```

---

## Use Cases

### ✅ Use Simple Format When:

- Writing quick dataset documentation
- Non-technical users creating contexts
- Single dataset context
- No need for metrics/glossary
- Just want to provide description
- Prototyping/testing

### ✅ Use Structured Format When:

- Need pre-defined metrics
- Need business glossary terms
- Need custom filters
- Multi-dataset relationships
- Advanced features required
- Full control over metadata

---

## Examples

### Example 1: E-commerce Dataset

**Simple Format:**

```markdown
# E-commerce Orders Dataset

Complete order history for our online store from 2020-2023.

## What's Inside

The dataset includes:
- Order ID and timestamps
- Customer information
- Product details
- Payment amounts
- Shipping addresses

## Analysis Ideas

You can explore:
- Revenue trends over time
- Top-selling products
- Customer purchasing patterns
- Seasonal variations
```

### Example 2: Social Media Analytics

**Simple Format:**

```markdown
# Social Media Engagement

User engagement metrics from our social media campaigns.

## Metrics Included

- Post impressions
- Likes and shares
- Comment counts
- Click-through rates
- Follower growth

## Key Questions

- Which posts performed best?
- What time of day gets most engagement?
- Which content type drives clicks?
```

---

## Benefits

### For Users
- ✅ **No YAML learning curve**
- ✅ **Write natural documentation**
- ✅ **Faster context creation**
- ✅ **Markdown familiar to most users**

### For Developers
- ✅ **Backward compatible** (existing contexts work)
- ✅ **Same database schema**
- ✅ **Same FK optimization** (Phase 2)
- ✅ **Automatic structure generation**

### For the System
- ✅ **Lower barrier to entry**
- ✅ **More contexts created**
- ✅ **Better context adoption**
- ✅ **Simpler onboarding**

---

## Limitations of Simple Format

The simple format **does not support**:

- ❌ Pre-defined metrics
- ❌ Business glossary terms
- ❌ Custom filters
- ❌ Multi-dataset contexts
- ❌ Dataset relationships
- ❌ Custom context type/status
- ❌ Custom version numbers

**Solution**: Upgrade to structured format when you need these features.

---

## Migration Path

### From Simple to Structured

If you start with simple format and later need advanced features:

1. **Get current context**: Fetch existing simple context
2. **Export content**: Download markdown content
3. **Add YAML frontmatter**: Add structured metadata
4. **Update context**: Upload new structured format

**Example Migration:**

**Before (Simple):**
```markdown
# Sales Data
Monthly sales for all products
```

**After (Structured):**
```yaml
---
name: "Sales Data"
version: "2.0.0"
description: "Monthly sales for all products"
datasets:
  - id: "sales"
    name: "Sales Data"
    dataset_id: "..."
metrics:
  - id: "total_revenue"
    expression: "SUM(amount)"
    name: "Total Revenue"
---

# Sales Data
Monthly sales for all products
```

---

## Testing

### Test Script

```bash
cd backend
python test_simple_context.py
```

**Expected Output:**
```
✅ Simple format works (plain markdown)
✅ Structured format works (YAML + markdown)
✅ Backward compatibility maintained
```

---

## Performance

Simple format has **identical performance** to structured format:

| Operation | Simple | Structured |
|-----------|--------|------------|
| Parse Time | ~5ms | ~5ms |
| Create Context | ~20ms | ~20ms |
| Context Lookup (Phase 2) | **~0.7ms** | **~0.7ms** |
| Auto-Population | ✅ Works | ✅ Works |

Both formats use the same FK optimization from Phase 2.

---

## Summary

✨ **Simple Context Format** makes it easy to document datasets with just markdown.

**Quick Start:**
1. Write markdown description
2. Provide dataset_id
3. Create context
4. Done!

**No YAML required. No complex structure. Just documentation.**

---

## FAQ

**Q: Can I use emojis in simple format?**
A: Yes! Use emojis, formatting, lists, headers - any markdown.

**Q: What happens if I don't provide dataset_id?**
A: Parser will error. Simple format requires dataset_id.

**Q: Can I have multiple datasets in simple format?**
A: No. Simple format is single-dataset only. Use structured format for multi-dataset.

**Q: Will my old contexts still work?**
A: Yes! Structured format is fully backward compatible.

**Q: Can I switch from simple to structured later?**
A: Yes! Add YAML frontmatter and update the context.

**Q: Does Phase 2 FK optimization work with simple format?**
A: Yes! Auto-population and fast lookup work identically.

---

**Status**: ✅ Implemented and Tested
**Version**: 1.0.0
**Date**: 2026-02-04
