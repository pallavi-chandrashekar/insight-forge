# How to Use Documentation Context for Better Analysis

## 🎯 Overview

Context files help the AI understand your data better by providing:
- **Business knowledge** - What the data means
- **Domain expertise** - Technical documentation
- **Column descriptions** - What each field represents
- **Relationships** - How data connects together

---

## 📖 Complete Workflow

### Step 1: Import Documentation (Done!)

You've already created contexts from URLs using Smart Import. Great!

**What you have:**
- Context: "PySpark Documentation" (or similar)
- Content: Documentation from the URL
- Status: Active

---

### Step 2: Link Context to Your Dataset

**Currently, generic documentation contexts are NOT automatically linked to datasets.**

You need to edit the context to specify which dataset(s) it applies to.

#### Option A: Edit Context to Add Dataset ID

1. **Go to Contexts page**
2. **Click on your context** (e.g., "PySpark Documentation")
3. **Click "Edit"**
4. **Add dataset information:**

```markdown
# PySpark Documentation

**Source:** https://spark.apache.org/docs/latest/api/python/index.html
**Imported:** Automatically from URL
**Type:** General Documentation

## Dataset: My PySpark Analysis (id: your-dataset-uuid-here)

This documentation applies to analyzing data using PySpark.

---

[Original documentation content...]
```

5. **Save**

**How to get your dataset ID:**
- Go to your dataset page
- Look at the URL: `http://localhost:5173/datasets/38875e33-0d72-4df6-bfaf-792e11f40015`
- The UUID is your dataset ID: `38875e33-0d72-4df6-bfaf-792e11f40015`

---

#### Option B: Create Dataset-Specific Context from Scratch

If you want to combine documentation with dataset-specific info:

1. **Go to "Create Context" page**
2. **Use this format:**

```markdown
# My Data Analysis Context

**Type:** Data Analysis with PySpark
**Version:** 1.0.0

## Dataset: Sales Data (id: your-dataset-uuid)

This dataset contains sales information analyzed using PySpark techniques.

## Column Descriptions

From PySpark documentation, these columns use standard patterns:
- `order_id`: Unique identifier (String type in PySpark)
- `customer_id`: Customer reference (String type)
- `order_date`: Timestamp (use `to_timestamp()` function)
- `total_amount`: Decimal (use `DecimalType` for precision)

## Analysis Patterns (from PySpark Docs)

**Aggregations:**
- Use `groupBy()` and `agg()` for summaries
- `df.groupBy("customer_id").agg(sum("total_amount"))`

**Date Operations:**
- Use `date_format()` for formatting
- `dayofweek()`, `month()`, `year()` for extraction

**Window Functions:**
- Use `Window.partitionBy()` for running calculations
- Example: Running totals, rankings

## PySpark Best Practices

[Paste relevant sections from the PySpark documentation here...]
```

3. **Save context**

---

### Step 3: Use Context in Queries

Once your context is linked to a dataset, the AI will automatically use it!

#### How It Works Automatically

When you use **Natural Language Visualization** (the NL viz feature we built in Phase 2), the system:

1. **Detects** you're querying a dataset
2. **Finds** the active context linked to that dataset
3. **Includes** context metadata in the AI prompt
4. **Generates** better visualizations based on the context

**No extra steps needed!** Just use the Visualize page.

---

## 🧪 Examples: Before vs After Context

### Example 1: Without Context

**Query:** "Show me sales by region"

**AI Thinking:**
- Dataset has columns: `region`, `sales`, `date`, `product`
- No business knowledge
- Generic chart

**Result:**
```
Simple bar chart:
- X-axis: region
- Y-axis: sales
- Generic title: "Sales by Region"
```

---

### Example 2: With PySpark Context

**Context includes:**
```markdown
## Best Practices from PySpark Docs

When aggregating sales data:
- Use `groupBy()` with `agg(sum())`
- Format currency with `format_number()`
- Sort by sales descending for better insights
```

**Query:** "Show me sales by region"

**AI Thinking:**
- Dataset has columns: region, sales, date, product
- Context says: Use groupBy and sort by sales descending
- Better insights from documentation

**Result:**
```
Enhanced bar chart:
- X-axis: region (sorted by sales)
- Y-axis: Total sales (formatted as currency)
- Title: "Total Sales by Region (Sorted by Revenue)"
- Better defaults based on PySpark best practices
```

---

### Example 3: Technical Context

**Context includes:**
```markdown
## PySpark Data Types

This dataset uses:
- `order_date`: TimestampType (requires `to_timestamp()` conversion)
- `total_amount`: DecimalType(10,2) for precision
- Avoid using `DoubleType` for money - use `DecimalType`
```

**Query:** "Show daily sales trend"

**Without context:**
- Might use double for amounts (loses precision)
- Generic date formatting

**With context:**
- Uses DecimalType for currency precision
- Proper timestamp handling
- Follows PySpark best practices

---

## 💡 Real-World Use Cases

### Use Case 1: Learning PySpark While Analyzing Data

**Scenario:** You're new to PySpark and want to analyze sales data.

**Setup:**
1. Import PySpark documentation via Smart Import
2. Link it to your sales dataset
3. Add notes about which PySpark functions apply to which columns

**Benefit:**
- AI suggests PySpark-appropriate visualizations
- You learn PySpark patterns while analyzing
- Documentation is always available as reference

**Example Query:**
```
"Show me customer lifetime value using PySpark window functions"
```

**AI Response:**
- Uses Window.partitionBy (from context)
- Suggests proper window function syntax
- Creates visualization following PySpark patterns

---

### Use Case 2: Domain-Specific Documentation

**Scenario:** You have a healthcare dataset and medical terminology documentation.

**Setup:**
1. Import medical terminology guide via Smart Import
2. Link to patient data dataset
3. Add medical term definitions to context

**Context Example:**
```markdown
## Medical Terminology

- **ICD-10**: International Classification of Diseases, 10th revision
- **CPT**: Current Procedural Terminology codes
- **Comorbidity**: Presence of multiple conditions

## Data Interpretation

- Age groups: Pediatric (<18), Adult (18-65), Senior (65+)
- BMI categories: Underweight (<18.5), Normal (18.5-24.9), Overweight (25-29.9), Obese (30+)
```

**Benefit:**
- AI understands medical terms
- Generates medically accurate visualizations
- Uses proper age groups and categories

**Example Query:**
```
"Show distribution of BMI categories by age group"
```

**AI Response:**
- Uses correct BMI category boundaries (from context)
- Groups ages properly (Pediatric, Adult, Senior)
- Creates medically appropriate visualization

---

### Use Case 3: API Documentation Context

**Scenario:** Analyzing API usage data with API documentation.

**Setup:**
1. Import API documentation
2. Link to API logs dataset
3. Document endpoint meanings and expected patterns

**Context Example:**
```markdown
## API Endpoints

- `/api/users` - User management (should have ~1000 requests/day)
- `/api/orders` - Order processing (should have ~500 requests/day)
- `/api/auth` - Authentication (high frequency expected)

## Expected Patterns

- Normal: 95% success rate (200 status)
- Alert if: >5% error rate (4xx, 5xx)
- Peak hours: 9 AM - 5 PM EST
```

**Benefit:**
- AI knows what's normal vs abnormal
- Suggests anomaly detection
- Interprets metrics correctly

**Example Query:**
```
"Show me which endpoints have unusual error rates"
```

**AI Response:**
- Knows normal is 95% success (from context)
- Flags endpoints with >5% errors
- Highlights anomalies based on documentation

---

## 🔧 Advanced: Programmatic Context Usage

### For Developers: Using Context in Custom Queries

If you're building custom features, here's how to use context programmatically:

```python
from app.services.context_service import ContextService

# In your query handler
context_service = ContextService(db)

# Find context for dataset
context = await context_service.find_active_context_by_dataset(
    dataset_id=your_dataset_id,
    user_id=current_user.id
)

if context:
    # Extract relevant information
    context_metadata = {
        "name": context.name,
        "description": context.description,
        "content": context.markdown_content,
        "datasets": context.datasets,
        "relationships": context.relationships
    }

    # Include in LLM prompt
    prompt = f"""
    Dataset schema: {schema}

    Context documentation:
    {context_metadata['content']}

    User query: {user_query}

    Generate response using the context documentation...
    """
```

---

## 📊 Measuring Context Impact

### How to Tell if Context is Being Used

1. **Check Query Response:**
   - Does it reference documentation terms?
   - Does it follow documented patterns?
   - Does it use domain-specific knowledge?

2. **Compare Results:**
   - Run query without context (deactivate context)
   - Run same query with context (activate context)
   - Compare quality of results

3. **Look for These Improvements:**
   - ✅ Better column understanding
   - ✅ Domain-appropriate aggregations
   - ✅ Proper data type handling
   - ✅ Business-rule-aware filtering
   - ✅ Technically accurate suggestions

---

## 🎯 Best Practices

### 1. Be Specific in Context

**Bad:**
```markdown
This is data about sales.
```

**Good:**
```markdown
## Sales Data Analysis (PySpark)

This dataset tracks e-commerce sales with:
- Daily granularity
- Multiple product categories
- Customer segmentation
- Regional breakdowns

Use PySpark's `groupBy()` and `agg()` for efficient aggregations.
For date analysis, use `date_format()` and window functions.
```

### 2. Include Relevant Examples

```markdown
## Example Queries (from Documentation)

**Total sales by region:**
```python
df.groupBy("region").agg(sum("sales").alias("total_sales"))
```

**Monthly trends:**
```python
df.groupBy(month("order_date")).agg(sum("sales"))
```
```

### 3. Update Context as You Learn

As you discover patterns in your data:
1. Edit your context
2. Add new insights
3. Document what works
4. Share with team

---

## 🚀 Quick Start Checklist

- [ ] Create context from documentation (Smart Import) ✅ You did this!
- [ ] Get your dataset ID from dataset URL
- [ ] Edit context to add dataset reference
- [ ] Test a query on the Visualize page
- [ ] Check if AI uses context information
- [ ] Refine context based on results
- [ ] Document patterns you discover

---

## 🆘 Troubleshooting

### Context Not Being Used?

**Check:**
1. Is context status "active"?
2. Is dataset ID correctly referenced in context?
3. Are you using the Natural Language Visualization feature? (Context auto-loads there)
4. Try deactivating and reactivating context

### How to Verify Context is Linked

**Query the database:**
```sql
SELECT id, name, datasets FROM contexts WHERE user_id = 'your-user-id';
```

**Or check in frontend:**
- Go to Contexts page
- Open your context
- Look at "Datasets" section
- Should show linked datasets

---

## 📝 Summary

### What Context Does
✅ Provides domain knowledge to AI
✅ Improves query understanding
✅ Generates better visualizations
✅ Enables learning while analyzing

### How to Use It
1. Import documentation (Smart Import) ✅
2. Link to dataset (edit context with dataset ID)
3. Query your data (use NL Visualization)
4. AI automatically uses context ✅

### Next Steps
1. Edit your PySpark context to add your dataset ID
2. Try a query on the Visualize page
3. See how context improves results
4. Iterate and refine!

---

**Your context is ready to use!** Just link it to your dataset and start querying. 🚀
