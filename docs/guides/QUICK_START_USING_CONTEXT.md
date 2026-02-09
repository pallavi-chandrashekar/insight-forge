# Quick Start: Using Context in 3 Steps

## 🎯 Goal
Make the AI understand your data better using documentation you imported.

---

## Step 1: Get Your Dataset ID (30 seconds)

1. Go to your **Datasets** page
2. Click on the dataset you want to analyze
3. Look at the browser URL bar:
   ```
   http://localhost:5173/datasets/38875e33-0d72-4df6-bfaf-792e11f40015
                                    ↑
                                    This is your dataset ID
   ```
4. **Copy** this UUID (the long string of letters and numbers)

---

## Step 2: Link Context to Dataset (2 minutes)

1. Go to **Contexts** page
2. Find your context (e.g., "PySpark Documentation")
3. Click **"Edit"** (or **"View"** then **"Edit"**)
4. **Add this section** at the top of your context:

```markdown
## Dataset: My Data Analysis (id: PASTE-YOUR-DATASET-ID-HERE)

This documentation applies to my data analysis.
```

**Example:**
```markdown
# PySpark Documentation

## Dataset: Sales Analysis (id: 38875e33-0d72-4df6-bfaf-792e11f40015)

This PySpark documentation helps analyze the sales dataset.

**Source:** https://spark.apache.org/docs/latest/api/python/index.html

[Rest of your imported documentation...]
```

5. Click **"Save"**

---

## Step 3: Test It! (1 minute)

1. Go to your **Dataset** page (the one you linked)
2. Click **"Visualize"** tab
3. Try a natural language query:
   ```
   Show me a trend analysis by date
   ```
4. Click **"Generate Visualization"**
5. ✅ **The AI will now use your PySpark documentation!**

---

## 🧪 How to Tell It's Working

### Before Context:
```
Query: "Show me sales by region"
Result: Basic bar chart with generic settings
```

### After Context:
```
Query: "Show me sales by region"
Result: Enhanced chart using PySpark best practices
- Sorted by value (from documentation)
- Proper aggregations (from documentation)
- Better defaults (from documentation)
```

---

## 💡 Example Queries to Try

Once your context is linked, try these:

```
"Show daily sales trend"
→ AI uses PySpark date functions from your docs

"Compare sales across regions"
→ AI uses PySpark groupBy patterns from your docs

"Find top 10 customers"
→ AI uses PySpark sorting/limiting from your docs
```

---

## 🎯 What Happens Behind the Scenes

```
You ask a question
   ↓
System finds your dataset
   ↓
System finds linked context
   ↓
System includes documentation in AI prompt
   ↓
AI generates better response using documentation
   ↓
You get improved visualization!
```

---

## ⚡ Pro Tips

### Tip 1: Add Column Descriptions
```markdown
## Columns in This Dataset

- `order_date`: Date of purchase (use PySpark date functions)
- `total_amount`: Sale amount in USD (use DecimalType)
- `region`: Sales region (use groupBy for aggregation)
```

### Tip 2: Add Expected Patterns
```markdown
## Expected Patterns

- Peak sales: December (holiday season)
- Typical order value: $50-$200
- Top region: Usually West Coast
```

### Tip 3: Add Business Rules
```markdown
## Business Rules

- Filter out orders < $10 (likely test data)
- Group regions: North (NY, MA), South (FL, TX), etc.
- Calculate metrics monthly, not daily
```

---

## 🔄 Update Context as You Learn

As you discover insights:
1. **Edit your context**
2. **Add new findings:**
   ```markdown
   ## Insights Discovered

   - Column `customer_type` has values: "new", "returning", "vip"
   - Sales spike on weekends
   - High correlation between region and product category
   ```
3. **Save**
4. Future queries will use this knowledge!

---

## 🆘 Troubleshooting

### "Not seeing any difference?"

**Check:**
- ✅ Did you add the dataset ID to the context?
- ✅ Is the context status "active"?
- ✅ Are you querying the correct dataset?
- ✅ Try a more complex query (context helps more with complexity)

**Format check:**
```markdown
## Dataset: My Dataset Name (id: uuid-here)
                                  ↑
                            Must say "id:" before the UUID
```

### "How do I know which dataset ID to use?"

Each dataset in your app has a unique ID. Steps:
1. Open the dataset you want to analyze
2. Look at the URL in your browser
3. Copy the UUID from the URL
4. Paste it in your context

---

## 📊 Example: Complete Context

Here's a complete example of a well-structured context:

```markdown
# PySpark Sales Analysis Documentation

## Dataset: E-commerce Sales (id: 38875e33-0d72-4df6-bfaf-792e11f40015)

This context provides PySpark best practices for analyzing e-commerce sales data.

## Data Description

- **Time range:** 2020-2024
- **Granularity:** Daily transactions
- **Size:** ~50K rows
- **Updates:** Monthly

## Column Descriptions

- `order_id`: Unique identifier (String)
- `order_date`: Transaction date (Timestamp - use `to_timestamp()`)
- `customer_id`: Customer identifier (String)
- `total_amount`: Order total in USD (Decimal - use `DecimalType(10,2)`)
- `region`: Sales region (String - values: North, South, East, West)
- `product_category`: Product type (String)

## PySpark Patterns to Use

### Aggregations
```python
# Total sales by region
df.groupBy("region").agg(sum("total_amount").alias("total_sales"))

# Monthly trends
df.groupBy(month("order_date")).agg(sum("total_amount"))
```

### Date Operations
```python
# Convert to timestamp
df.withColumn("order_date", to_timestamp("order_date"))

# Extract date parts
df.withColumn("month", month("order_date"))
  .withColumn("year", year("order_date"))
```

### Window Functions
```python
# Running total
from pyspark.sql.window import Window
window_spec = Window.partitionBy("customer_id").orderBy("order_date")
df.withColumn("running_total", sum("total_amount").over(window_spec))
```

## Business Rules

- Exclude orders < $10 (test transactions)
- Peak season: November-December (+40% sales)
- VIP customers: Lifetime value > $10,000

## Analysis Best Practices (from PySpark Docs)

- Use `cache()` for repeated operations
- Use `coalesce()` for optimal partitioning
- Prefer `agg()` over multiple `withColumn()` calls
- Use broadcast joins for small dimension tables

---

**Documentation Source:** https://spark.apache.org/docs/latest/api/python/index.html
**Last Updated:** 2026-02-05
```

---

## ✅ Success Checklist

- [ ] Got dataset ID from URL
- [ ] Edited context to add dataset reference
- [ ] Saved context
- [ ] Tested a query on Visualize page
- [ ] Saw improved results! 🎉

---

## 🚀 Next Steps

1. **Try it now:** Follow the 3 steps above
2. **Test queries:** See how context improves responses
3. **Iterate:** Add more details to your context as you learn
4. **Share:** Create contexts for your team to use

**Your documentation is now powering better AI responses!** 🎉

---

## 📚 Learn More

- **Full guide:** See `HOW_TO_USE_CONTEXT.md`
- **Advanced usage:** Context with relationships, metrics, business rules
- **Examples:** Real-world use cases and patterns

**Questions?** Ask in the Issues or check the documentation!
