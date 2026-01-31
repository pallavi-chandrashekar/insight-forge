# Query Engine - Manual Testing Guide

**Quick Reference for Manual QA Testing**

---

## Prerequisites

1. Backend server running on `http://localhost:8000`
2. Frontend running on `http://localhost:5173`
3. Test account credentials:
   - Email: `test@example.com`
   - Password: `testpassword123`
4. Test data files in `/tmp/` directory

---

## Setup Test Environment

### Step 1: Generate Test Data
```bash
cd backend
python tests/test_data.py
```

This creates:
- ✅ `test_products.csv` - 10 products
- ✅ `test_sales.csv` - 20 orders
- ✅ `test_customers.csv` - 10 customers
- ✅ `test_employees.csv` - 15 employees

### Step 2: Start Services
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database (if not running)
brew services start postgresql
```

---

## Test Scenario 1: SQL Query Execution

### Test Case: Basic Product Query

**Goal:** Execute a SQL query to find expensive products

**Steps:**

1. **Login**
   - Navigate to `http://localhost:5173/login`
   - Enter credentials
   - Click "Login"
   - 📸 **Screenshot 1.1:** Login page

2. **Upload Dataset**
   - Click "Datasets" in navigation
   - Click "Upload Dataset" button
   - Select `test_products.csv`
   - Name: "Products"
   - Click "Upload"
   - Wait for upload confirmation
   - 📸 **Screenshot 1.2:** Upload dialog
   - 📸 **Screenshot 1.3:** Upload success message

3. **Navigate to Query Page**
   - Click "Query" in navigation
   - Select "Products" dataset from dropdown
   - Select "SQL" query type
   - 📸 **Screenshot 1.4:** Query page

4. **Write SQL Query**
   - In SQL editor, enter:
     ```sql
     SELECT
         product_name,
         category,
         price,
         stock,
         rating
     FROM df
     WHERE price > 100
     ORDER BY price DESC
     ```
   - 📸 **Screenshot 1.5:** SQL query entered

5. **Execute Query**
   - Click "Execute" button
   - Wait for results
   - 📸 **Screenshot 1.6:** Loading indicator
   - 📸 **Screenshot 1.7:** Query results table

6. **Verify Results**
   - ✅ Check 6 products returned
   - ✅ All prices > $100
   - ✅ Sorted by price (highest first)
   - ✅ Execution time displayed
   - 📸 **Screenshot 1.8:** Results with execution time

7. **Save Query**
   - Enter name: "Expensive Products"
   - Click "Save Query"
   - See success message
   - 📸 **Screenshot 1.9:** Save dialog
   - 📸 **Screenshot 1.10:** Success message

**Expected Results:**
| Product Name | Category | Price | Stock | Rating |
|--------------|----------|-------|-------|--------|
| Laptop Pro 15 | Computers | $1,299.99 | 50 | 4.5 |
| Tablet 10" | Computers | $499.99 | 60 | 4.5 |
| 27" Monitor | Monitors | $349.99 | 75 | 4.6 |
| Wireless Headphones | Audio | $199.99 | 90 | 4.8 |
| External SSD 1TB | Storage | $149.99 | 100 | 4.6 |

---

## Test Scenario 2: Aggregation Query

### Test Case: Category Analysis

**Goal:** Analyze products by category

**Steps:**

1. **Navigate to Query Page**
   - Select "Products" dataset
   - Select "SQL" query type

2. **Write Aggregation Query**
   ```sql
   SELECT
       category,
       COUNT(*) as product_count,
       AVG(price) as avg_price,
       MIN(price) as min_price,
       MAX(price) as max_price,
       SUM(stock) as total_stock
   FROM df
   GROUP BY category
   ORDER BY avg_price DESC
   ```
   - 📸 **Screenshot 2.1:** Aggregation query

3. **Execute and Verify**
   - Click "Execute"
   - 📸 **Screenshot 2.2:** Aggregation results

**Expected Results:**
| Category | Product Count | Avg Price | Min Price | Max Price | Total Stock |
|----------|---------------|-----------|-----------|-----------|-------------|
| Computers | 2 | $899.99 | $499.99 | $1,299.99 | 110 |
| Monitors | 1 | $349.99 | $349.99 | $349.99 | 75 |
| Audio | 1 | $199.99 | $199.99 | $199.99 | 90 |

---

## Test Scenario 3: Pandas Operations

### Test Case: Filter and Sort Products

**Goal:** Use Pandas operations to filter and sort

**Steps:**

1. **Navigate to Query Page**
   - Select "Products" dataset
   - Select "Pandas Operations" query type
   - 📸 **Screenshot 3.1:** Pandas operations interface

2. **Add Filter Operation**
   - Click "Add Operation"
   - Select "Filter"
   - Condition: `price > 50`
   - Click "Add"
   - 📸 **Screenshot 3.2:** Filter operation added

3. **Add Sort Operation**
   - Click "Add Operation"
   - Select "Sort"
   - Column: `price`
   - Order: Descending
   - Click "Add"
   - 📸 **Screenshot 3.3:** Sort operation added

4. **Add Limit Operation**
   - Click "Add Operation"
   - Select "Head"
   - N: `5`
   - Click "Add"
   - 📸 **Screenshot 3.4:** Head operation added

5. **Review Operations Chain**
   - See 3 operations listed
   - 📸 **Screenshot 3.5:** Operations chain view

6. **Execute Operations**
   - Click "Execute"
   - View results
   - 📸 **Screenshot 3.6:** Pandas results

7. **View Generated Code**
   - Click "Show Code" button
   - See equivalent Pandas code
   - 📸 **Screenshot 3.7:** Generated Pandas code

**Expected Results:**
- 5 products returned
- All prices > $50
- Sorted by price descending
- Top product: Laptop Pro 15 ($1,299.99)

---

## Test Scenario 4: Natural Language Query

### Test Case: Ask Question in Plain English

**Goal:** Query data using natural language

**Steps:**

1. **Navigate to Query Page**
   - Select "Sales" dataset (upload first if not exists)
   - Select "Natural Language" query type
   - 📸 **Screenshot 4.1:** NL query interface

2. **Ask Question**
   - In text field, enter:
     > "What are the top 5 customers by total spending?"
   - 📸 **Screenshot 4.2:** Question entered

3. **Submit Question**
   - Click "Ask" button
   - Wait for LLM to process
   - 📸 **Screenshot 4.3:** Processing indicator

4. **Review Generated SQL**
   - See auto-generated SQL query
   - 📸 **Screenshot 4.4:** Generated SQL display

5. **Execute Query**
   - Click "Execute Query" button
   - View results
   - 📸 **Screenshot 4.5:** NL query results

6. **Verify Results**
   - Check top customers listed
   - Verify spending amounts
   - 📸 **Screenshot 4.6:** Results table

**Expected Results:**
- SQL generated correctly
- Top 5 customers returned
- Spending totals accurate
- Query explanation provided

---

## Test Scenario 5: Query History

### Test Case: View and Rerun Past Queries

**Goal:** Access and reuse query history

**Steps:**

1. **Navigate to History Tab**
   - Click "Query" in navigation
   - Click "History" tab
   - 📸 **Screenshot 5.1:** History page

2. **View Query List**
   - See all past queries
   - Check sorting (newest first)
   - 📸 **Screenshot 5.2:** Query history list

3. **Filter by Dataset**
   - Select "Products" from dataset filter
   - See filtered queries
   - 📸 **Screenshot 5.3:** Filtered history

4. **View Query Details**
   - Click on "Expensive Products" query
   - Modal opens with details
   - 📸 **Screenshot 5.4:** Query details modal

5. **Rerun Query**
   - Click "Run Again" button
   - See updated results
   - 📸 **Screenshot 5.5:** Rerun results

6. **Edit and Save As New**
   - Click "Edit" button
   - Modify query
   - Click "Save As"
   - Name: "Modified Query"
   - 📸 **Screenshot 5.6:** Save As dialog

**Expected Results:**
- All queries accessible
- Can filter by dataset
- Can rerun any query
- Can create variations

---

## Test Scenario 6: Error Handling

### Test Case: Invalid SQL Query

**Goal:** Verify error handling

**Steps:**

1. **Write Invalid Query**
   ```sql
   SELECT * FORM df
   ```
   (Note: FORM instead of FROM)
   - 📸 **Screenshot 6.1:** Invalid SQL

2. **Execute Query**
   - Click "Execute"
   - 📸 **Screenshot 6.2:** Error message

3. **Verify Error Handling**
   - ✅ Error message displayed
   - ✅ No crash
   - ✅ Can edit and retry
   - 📸 **Screenshot 6.3:** Error state

**Expected Results:**
- Error: "SQL syntax error near 'FORM'"
- Query not saved with error
- User can correct and retry

---

## Test Scenario 7: Column Selection

### Test Case: Select Specific Columns

**Goal:** Query specific columns only

**Steps:**

1. **Write Column-Specific Query**
   ```sql
   SELECT product_name, price, rating
   FROM df
   WHERE rating > 4.5
   ORDER BY rating DESC
   ```
   - 📸 **Screenshot 7.1:** Column selection query

2. **Execute and Verify**
   - Only 3 columns in results
   - All ratings > 4.5
   - 📸 **Screenshot 7.2:** Column-specific results

**Expected Results:**
| Product Name | Price | Rating |
|--------------|-------|--------|
| Wireless Headphones | $199.99 | 4.8 |
| Mechanical Keyboard | $89.99 | 4.7 |

---

## Test Scenario 8: Complex WHERE Clause

### Test Case: Multiple Conditions

**Goal:** Test complex filtering

**Steps:**

1. **Write Complex Query**
   ```sql
   SELECT *
   FROM df
   WHERE (price > 100 OR stock < 100)
       AND category IN ('Computers', 'Monitors')
   ORDER BY price DESC
   ```
   - 📸 **Screenshot 8.1:** Complex WHERE query

2. **Execute and Verify**
   - Multiple conditions applied
   - Correct filtering
   - 📸 **Screenshot 8.2:** Complex filter results

**Expected Results:**
- Products matching complex criteria
- Computers and Monitors only
- Either expensive OR low stock

---

## Test Scenario 9: Export Results

### Test Case: Download Query Results

**Goal:** Export results to CSV

**Steps:**

1. **Execute Any Query**
   - Run a query with results

2. **Export Results**
   - Click "Export" button
   - Select "CSV"
   - 📸 **Screenshot 9.1:** Export options

3. **Verify Download**
   - Check Downloads folder
   - Open CSV in Excel/Numbers
   - Verify data integrity
   - 📸 **Screenshot 9.2:** Downloaded CSV

**Expected Results:**
- CSV file downloaded
- All columns present
- Data matches query results

---

## Test Scenario 10: Performance Test

### Test Case: Large Dataset Query

**Goal:** Test performance with larger data

**Steps:**

1. **Upload Large Dataset**
   - Use dataset with 1000+ rows
   - 📸 **Screenshot 10.1:** Large upload

2. **Execute Query**
   - Run aggregation query
   - Note execution time
   - 📸 **Screenshot 10.2:** Execution time

**Expected Results:**
- Query completes < 2 seconds
- No timeout errors
- Results display correctly

---

## Checklist for Complete Testing

### Functional Tests
- [ ] SQL query execution works
- [ ] Pandas operations work
- [ ] Natural language queries work
- [ ] Query history accessible
- [ ] Query saving works
- [ ] Query rerunning works
- [ ] Error handling works
- [ ] Results export works

### UI/UX Tests
- [ ] Query editor has syntax highlighting
- [ ] Auto-complete for column names
- [ ] Results table is paginated
- [ ] Loading indicators display
- [ ] Error messages are clear
- [ ] Responsive design works
- [ ] Keyboard shortcuts work

### Data Validation
- [ ] All query types return correct results
- [ ] Aggregations calculate correctly
- [ ] Filters apply properly
- [ ] Sorting works correctly
- [ ] NULL values handled
- [ ] Special characters handled

### Performance
- [ ] Simple queries < 100ms
- [ ] Complex queries < 500ms
- [ ] Large results paginated
- [ ] No memory leaks
- [ ] Concurrent queries supported

### Security
- [ ] Authentication required
- [ ] Users see only their data
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Rate limiting works

---

## Bug Reporting Template

When you find a bug, document it:

**Bug ID:** BUG-QE-001
**Severity:** High/Medium/Low
**Title:** Brief description
**Steps to Reproduce:**
1. Step 1
2. Step 2
3. ...

**Expected Result:** What should happen
**Actual Result:** What actually happened
**Screenshot:** [Attach screenshot]
**Browser:** Chrome 120 / Firefox 121 / Safari 17
**Date Found:** 2025-01-26
**Tester:** Your name

---

## Contact

**Questions?** Contact the development team:
- Engineering Lead: eng-lead@company.com
- QA Manager: qa@company.com
- Slack: #insightforge-dev

---

**Document Version:** 1.0
**Last Updated:** 2025-01-26
**Next Review:** Weekly during testing phase
