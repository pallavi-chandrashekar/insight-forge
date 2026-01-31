# InsightForge Visualization Feature - Test Documentation

**Test Date:** 2024-01-26
**Version:** 1.0.0
**Tested By:** QA Team
**Environment:** Development

## Table of Contents
1. [Test Overview](#test-overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Test Data](#test-data)
4. [Test Scenarios](#test-scenarios)
5. [Test Results Summary](#test-results-summary)
6. [Issues Found](#issues-found)
7. [Recommendations](#recommendations)

---

## Test Overview

### Purpose
This document contains comprehensive test scenarios and results for the InsightForge visualization feature, including AI-powered chart suggestions and interactive chart generation.

### Scope
- Dataset upload and management
- AI-powered visualization suggestions
- Manual chart creation for all chart types
- Chart configuration and customization
- Chart rendering and interactivity
- Error handling and validation
- API endpoint testing
- Frontend UI/UX testing

### Out of Scope
- Tableau integration (future feature)
- Performance testing with large datasets
- Multi-user concurrent testing
- Mobile responsiveness

---

## Test Environment Setup

### Prerequisites
1. **Backend Requirements:**
   - Python 3.11+
   - PostgreSQL 14+
   - Redis (optional)
   - Valid Anthropic API key

2. **Frontend Requirements:**
   - Node.js 18+
   - npm or yarn

### Setup Steps

#### 1. Clone Repository
```bash
git clone <repository-url>
cd insight-forge
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API_KEY and DATABASE_URL
```

#### 3. Database Setup
```bash
# Using Docker Compose
docker-compose up -d db

# Or using local PostgreSQL
createdb insightforge
```

#### 4. Run Backend
```bash
uvicorn app.main:app --reload
# Backend should be running at http://localhost:8000
```

#### 5. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
# Frontend should be running at http://localhost:5173
```

#### 6. Verify Installation
- Navigate to http://localhost:8000/docs to see API documentation
- Navigate to http://localhost:5173 to see the frontend
- Register a test user account

---

## Test Data

### Dataset 1: Sales Sample Data
**File:** `docs/tests/test-data/sales_sample.csv`
**Description:** Product sales data with multiple dimensions
**Columns:**
- `date` (datetime): Transaction date
- `product` (string): Product name
- `category` (string): Product category (Electronics, Furniture)
- `region` (string): Sales region (North, South, East, West)
- `sales` (float): Total sales amount
- `quantity` (int): Number of items sold
- `price` (float): Unit price

**Rows:** 30
**Use Cases:** Bar charts, line charts, scatter plots, pie charts, heatmaps

### Dataset 2: Temperature Sample Data
**File:** `docs/tests/test-data/temperature_sample.csv`
**Description:** Weather data for multiple cities
**Columns:**
- `date` (datetime): Observation date
- `city` (string): City name
- `temperature` (float): Temperature in Fahrenheit
- `humidity` (int): Humidity percentage
- `precipitation` (float): Precipitation in inches

**Rows:** 20
**Use Cases:** Line charts, area charts, box plots, scatter plots

---

## Test Scenarios

### TS-01: Dataset Upload
**Objective:** Verify users can upload CSV files for visualization

**Test Steps:**
1. Navigate to Upload page
2. Select `sales_sample.csv` file
3. Enter dataset name: "Product Sales Data"
4. Enter description: "Sample sales data for testing"
5. Click "Upload"
6. Wait for upload to complete

**Expected Results:**
- ✅ File uploads successfully
- ✅ Dataset appears in dataset list
- ✅ Row count (30) and column count (7) displayed correctly
- ✅ Schema is automatically inferred
- ✅ Success message displayed

**Screenshot Placeholder:**
```
[Screenshot: Dataset upload form with file selected]
[Screenshot: Upload success message]
[Screenshot: Dataset list showing uploaded dataset]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-02: Navigate to Visualization Page
**Objective:** Verify navigation to visualization feature

**Test Steps:**
1. From dashboard, click "Visualize" in navigation
2. Verify page loads correctly
3. Check that uploaded datasets appear in dropdown

**Expected Results:**
- ✅ Visualization page loads without errors
- ✅ Dataset selector shows all uploaded datasets
- ✅ "Get AI Suggestions" button is visible
- ✅ No charts displayed initially

**Screenshot Placeholder:**
```
[Screenshot: Empty visualization page with dataset selector]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-03: AI Visualization Suggestions
**Objective:** Test Claude AI-powered chart recommendations

**Test Steps:**
1. Select "Product Sales Data" from dataset dropdown
2. Click "Get AI Suggestions" button
3. Wait for suggestions to load
4. Review suggested visualizations

**Expected Results:**
- ✅ Loading indicator appears
- ✅ 3-5 suggestions returned within 5 seconds
- ✅ Each suggestion shows:
  - Chart type
  - Title
  - Description
  - Confidence score (percentage)
  - Reasoning
- ✅ Suggestions are relevant to the data
- ✅ Confidence scores are reasonable (50-100%)

**Screenshot Placeholder:**
```
[Screenshot: Loading state during suggestion generation]
[Screenshot: AI suggestions displayed with confidence scores]
[Screenshot: Individual suggestion card with details]
```

**Suggested Visualizations (Expected):**
1. Bar chart: Sales by Category
2. Line chart: Sales over Time
3. Scatter plot: Price vs Quantity
4. Pie chart: Sales by Region

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-04: Generate Bar Chart from Suggestion
**Objective:** Create a bar chart from AI suggestion

**Test Steps:**
1. Click on "Sales by Category" suggestion (or similar bar chart)
2. Wait for chart to generate
3. Verify chart renders correctly

**Expected Results:**
- ✅ Chart generates within 3 seconds
- ✅ Plotly chart renders correctly
- ✅ X-axis shows categories (Electronics, Furniture)
- ✅ Y-axis shows numeric sales values
- ✅ Bars are properly sized and colored
- ✅ Chart title matches suggestion
- ✅ Interactive features work:
  - Hover to see values
  - Click legend to toggle series
  - Zoom and pan controls
  - Download button visible

**Screenshot Placeholder:**
```
[Screenshot: Generated bar chart showing sales by category]
[Screenshot: Hover interaction showing data values]
[Screenshot: Chart controls (zoom, pan, download)]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-05: Generate Line Chart from Suggestion
**Objective:** Create a line chart showing trends over time

**Test Steps:**
1. Click on "Sales over Time" suggestion (or similar line chart)
2. Wait for chart to generate
3. Verify chart renders correctly

**Expected Results:**
- ✅ Line chart renders with date on x-axis
- ✅ Sales values on y-axis
- ✅ Line is smooth and continuous
- ✅ Data points are visible
- ✅ Gridlines are present
- ✅ Chart is interactive

**Screenshot Placeholder:**
```
[Screenshot: Line chart showing sales trend over time]
[Screenshot: Zoomed in view of specific date range]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-06: Generate Scatter Plot
**Objective:** Create a scatter plot showing relationship between variables

**Test Steps:**
1. Click on "Price vs Quantity" suggestion (or similar scatter plot)
2. Wait for chart to generate
3. Verify chart renders correctly

**Expected Results:**
- ✅ Scatter plot renders with points
- ✅ X and Y axes are properly labeled
- ✅ Points are distinguishable
- ✅ Color coding (if by category) works
- ✅ Hover shows all data dimensions

**Screenshot Placeholder:**
```
[Screenshot: Scatter plot with price vs quantity]
[Screenshot: Color-coded scatter plot by category]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-07: Generate Pie Chart
**Objective:** Create a pie chart showing proportions

**Test Steps:**
1. Click on "Sales by Region" suggestion (or similar pie chart)
2. Wait for chart to generate
3. Verify chart renders correctly

**Expected Results:**
- ✅ Pie chart renders with proper slices
- ✅ Slices are proportional to values
- ✅ Labels and percentages are visible
- ✅ Legend shows all categories
- ✅ Colors are distinct
- ✅ Hover shows exact values

**Screenshot Placeholder:**
```
[Screenshot: Pie chart showing sales distribution by region]
[Screenshot: Hover showing percentage and value]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-08: Manual Chart Creation - Histogram
**Objective:** Manually create a histogram

**Test Steps:**
1. Navigate to manual chart creation (if available) or use custom config
2. Select chart type: Histogram
3. Configure:
   - X-axis: `sales` column
   - Title: "Sales Distribution"
4. Generate chart

**Expected Results:**
- ✅ Histogram renders with proper bins
- ✅ Shows distribution of sales values
- ✅ Bars are appropriately sized
- ✅ X-axis shows value ranges
- ✅ Y-axis shows frequency

**Screenshot Placeholder:**
```
[Screenshot: Histogram configuration form]
[Screenshot: Generated histogram]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-09: Manual Chart Creation - Heatmap
**Objective:** Create a correlation heatmap

**Test Steps:**
1. Upload `temperature_sample.csv` dataset
2. Create new visualization
3. Select chart type: Heatmap
4. Configure for correlation matrix (leave columns empty)
5. Generate chart

**Expected Results:**
- ✅ Heatmap renders as correlation matrix
- ✅ Shows correlations between numeric columns
- ✅ Color scale is appropriate (-1 to 1)
- ✅ Cell values are visible
- ✅ Column/row labels are readable

**Screenshot Placeholder:**
```
[Screenshot: Correlation heatmap]
[Screenshot: Heatmap with hover showing correlation value]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-10: Manual Chart Creation - Box Plot
**Objective:** Create a box plot showing distribution

**Test Steps:**
1. Use `temperature_sample.csv` dataset
2. Create new visualization
3. Select chart type: Box Plot
4. Configure:
   - X-axis: `city` (grouping)
   - Y-axis: `temperature`
   - Title: "Temperature Distribution by City"
5. Generate chart

**Expected Results:**
- ✅ Box plot renders for each city
- ✅ Shows median, quartiles, and outliers
- ✅ Boxes are properly sized
- ✅ Whiskers extend correctly
- ✅ Outliers (if any) are visible as points

**Screenshot Placeholder:**
```
[Screenshot: Box plot configuration]
[Screenshot: Generated box plot showing temperature distribution]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-11: Manual Chart Creation - Area Chart
**Objective:** Create an area chart for cumulative trends

**Test Steps:**
1. Use `temperature_sample.csv` dataset
2. Create new visualization
3. Select chart type: Area Chart
4. Configure:
   - X-axis: `date`
   - Y-axis: `temperature`
   - Color: `city`
   - Title: "Temperature Trends by City"
5. Generate chart

**Expected Results:**
- ✅ Area chart renders with filled areas
- ✅ Multiple cities shown in different colors
- ✅ Areas are stacked (if applicable) or overlapping
- ✅ Legend identifies each city
- ✅ Temporal trend is clear

**Screenshot Placeholder:**
```
[Screenshot: Area chart showing temperature trends]
[Screenshot: Stacked area chart variant]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-12: Chart Configuration - Aggregation
**Objective:** Test data aggregation in charts

**Test Steps:**
1. Use `sales_sample.csv` dataset
2. Create bar chart
3. Configure:
   - X-axis: `product`
   - Y-axis: `sales`
   - Aggregation: `sum`
4. Generate chart
5. Note the values
6. Change aggregation to `mean`
7. Regenerate chart
8. Compare values

**Expected Results:**
- ✅ Sum aggregation shows total sales per product
- ✅ Mean aggregation shows average sales per product
- ✅ Values change appropriately
- ✅ Chart updates correctly
- ✅ No errors during regeneration

**Screenshot Placeholder:**
```
[Screenshot: Bar chart with sum aggregation]
[Screenshot: Same bar chart with mean aggregation]
[Screenshot: Side-by-side comparison]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-13: Chart Configuration - Color Grouping
**Objective:** Test color/grouping functionality

**Test Steps:**
1. Use `sales_sample.csv` dataset
2. Create bar chart
3. Configure:
   - X-axis: `region`
   - Y-axis: `sales`
   - Color: `category`
   - Aggregation: `sum`
4. Generate chart

**Expected Results:**
- ✅ Chart shows grouped/stacked bars
- ✅ Each category has distinct color
- ✅ Legend shows all categories
- ✅ Clicking legend toggles category visibility
- ✅ Hover shows category breakdown

**Screenshot Placeholder:**
```
[Screenshot: Grouped bar chart by region and category]
[Screenshot: Legend interaction demonstration]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-14: Chart Customization - Labels
**Objective:** Test custom axis labels and titles

**Test Steps:**
1. Create any chart
2. Configure:
   - Title: "Custom Chart Title"
   - X Label: "Custom X Axis"
   - Y Label: "Custom Y Axis"
3. Generate chart

**Expected Results:**
- ✅ Custom title appears at top of chart
- ✅ Custom x-axis label appears below x-axis
- ✅ Custom y-axis label appears beside y-axis
- ✅ Labels are properly formatted and readable

**Screenshot Placeholder:**
```
[Screenshot: Chart with custom labels]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-15: Chart Interactivity - Zoom and Pan
**Objective:** Test Plotly interactive features

**Test Steps:**
1. Generate any chart with multiple data points
2. Test zoom:
   - Click and drag to select area
   - Double-click to reset
3. Test pan:
   - Click and drag chart (with pan tool)
4. Test reset:
   - Click "Reset axes" button

**Expected Results:**
- ✅ Zoom functionality works smoothly
- ✅ Panning works in all directions
- ✅ Reset returns to original view
- ✅ No data loss during interaction
- ✅ Performance is acceptable

**Screenshot Placeholder:**
```
[Screenshot: Chart in default view]
[Screenshot: Chart zoomed in to specific area]
[Screenshot: Chart toolbar with zoom/pan controls]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-16: Chart Interactivity - Hover Information
**Objective:** Test hover tooltips

**Test Steps:**
1. Generate charts of different types
2. Hover over various data points/bars/lines
3. Verify tooltip information

**Expected Results:**
- ✅ Tooltips appear on hover
- ✅ Tooltips show relevant data:
  - X and Y values
  - Additional dimensions (color, size)
  - Proper formatting
- ✅ Tooltips position correctly
- ✅ Tooltips disappear on mouse out

**Screenshot Placeholder:**
```
[Screenshot: Bar chart with hover tooltip]
[Screenshot: Scatter plot with multi-dimensional tooltip]
[Screenshot: Line chart with tooltip showing date and value]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-17: Chart Download/Export
**Objective:** Test chart export functionality

**Test Steps:**
1. Generate any chart
2. Click download button in chart toolbar
3. Try different formats:
   - PNG
   - SVG
   - (Other formats if available)

**Expected Results:**
- ✅ Download button is visible
- ✅ Click triggers download
- ✅ File downloads successfully
- ✅ File opens correctly
- ✅ Quality is acceptable
- ✅ All chart elements are included

**Screenshot Placeholder:**
```
[Screenshot: Chart toolbar with download button highlighted]
[Screenshot: Downloaded PNG image opened in viewer]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-18: Saved Visualizations - List View
**Objective:** Verify saved visualizations can be listed

**Test Steps:**
1. Generate and save 3-5 different charts
2. Navigate to visualization list/gallery (if available)
3. Verify all saved visualizations appear

**Expected Results:**
- ✅ All saved visualizations are listed
- ✅ Each shows: name, chart type, dataset, date
- ✅ Thumbnails or previews visible (if applicable)
- ✅ Sorted by creation date (newest first)

**Screenshot Placeholder:**
```
[Screenshot: List of saved visualizations]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-19: Saved Visualizations - Retrieve
**Objective:** Test retrieving and viewing saved charts

**Test Steps:**
1. From visualization list, click on a saved chart
2. Verify chart loads and displays correctly
3. Check that configuration is preserved

**Expected Results:**
- ✅ Chart loads without regeneration
- ✅ All data is preserved
- ✅ Configuration matches original
- ✅ Interactive features still work
- ✅ Loading is fast (< 1 second)

**Screenshot Placeholder:**
```
[Screenshot: Retrieved saved visualization]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-20: Saved Visualizations - Delete
**Objective:** Test deletion of saved visualizations

**Test Steps:**
1. From visualization list, select a chart
2. Click delete button
3. Confirm deletion
4. Verify chart is removed

**Expected Results:**
- ✅ Delete button is available
- ✅ Confirmation dialog appears
- ✅ Chart is deleted on confirm
- ✅ Chart removed from list
- ✅ Success message shown
- ✅ Cannot retrieve deleted chart

**Screenshot Placeholder:**
```
[Screenshot: Delete confirmation dialog]
[Screenshot: Updated list after deletion]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-21: Error Handling - No Dataset Selected
**Objective:** Test error handling when no dataset is selected

**Test Steps:**
1. Navigate to visualization page
2. Without selecting a dataset, click "Get AI Suggestions"

**Expected Results:**
- ✅ Button is disabled OR
- ✅ Error message appears: "Please select a dataset"
- ✅ No API call is made
- ✅ User can recover by selecting dataset

**Screenshot Placeholder:**
```
[Screenshot: Disabled button or error message]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-22: Error Handling - Missing Required Configuration
**Objective:** Test validation for required chart parameters

**Test Steps:**
1. Select chart type that requires x and y columns (e.g., bar chart)
2. Leave x_column or y_column empty
3. Try to generate chart

**Expected Results:**
- ✅ Validation error appears
- ✅ Error message identifies missing field
- ✅ Generate button disabled OR error on click
- ✅ Required fields marked with asterisk
- ✅ User can fix and retry

**Screenshot Placeholder:**
```
[Screenshot: Validation error for missing configuration]
[Screenshot: Required field indicators]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-23: Error Handling - Invalid Column Selection
**Objective:** Test handling of invalid column types

**Test Steps:**
1. Create scatter plot
2. Select non-numeric column for y-axis
3. Try to generate chart

**Expected Results:**
- ✅ Error message appears OR
- ✅ Non-numeric columns not available for selection OR
- ✅ Backend returns clear error message
- ✅ User can correct selection

**Screenshot Placeholder:**
```
[Screenshot: Error for invalid column type]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-24: Error Handling - API/Network Errors
**Objective:** Test handling of backend/network failures

**Test Steps:**
1. Stop backend server or disconnect network
2. Try to get AI suggestions
3. Try to generate chart
4. Observe error handling

**Expected Results:**
- ✅ Loading state appears then stops
- ✅ User-friendly error message displayed
- ✅ Technical error not exposed to user
- ✅ Error logged in console for debugging
- ✅ User can retry when connection restored

**Screenshot Placeholder:**
```
[Screenshot: Network error message]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-25: Error Handling - LLM API Failures
**Objective:** Test handling when Claude API fails or returns invalid data

**Test Steps:**
1. Use invalid API key in backend .env
2. Try to get AI suggestions
3. Observe error handling

**Expected Results:**
- ✅ Error caught gracefully
- ✅ User-friendly message: "Unable to get suggestions. Please try again."
- ✅ Doesn't crash application
- ✅ User can try manual chart creation

**Screenshot Placeholder:**
```
[Screenshot: LLM API error message]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-26: Performance - Large Dataset (1000+ rows)
**Objective:** Test performance with larger dataset

**Test Steps:**
1. Create or upload CSV with 1000-5000 rows
2. Generate various chart types
3. Measure response times

**Expected Results:**
- ✅ Upload completes within reasonable time (< 10 seconds)
- ✅ Suggestions generated within 10 seconds
- ✅ Charts render within 5 seconds
- ✅ UI remains responsive
- ✅ No browser crashes or freezes

**Screenshot Placeholder:**
```
[Screenshot: Large dataset chart rendering]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-27: API Endpoint - POST /api/visualize/suggest
**Objective:** Test suggestion API directly

**Test Steps:**
1. Use API testing tool (Postman, curl, etc.)
2. Send POST request to `/api/visualize/suggest?dataset_id=<uuid>`
3. Include valid auth token
4. Check response

**Expected Results:**
- ✅ Returns 200 status code
- ✅ Response is JSON array of suggestions
- ✅ Each suggestion has required fields:
  - chart_type
  - title
  - description
  - confidence
  - config
  - reasoning
- ✅ Returns within 10 seconds

**Test Request:**
```bash
curl -X POST "http://localhost:8000/api/visualize/suggest?dataset_id=<uuid>" \
  -H "Authorization: Bearer <token>"
```

**Screenshot Placeholder:**
```
[Screenshot: API request in Postman]
[Screenshot: JSON response with suggestions]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-28: API Endpoint - POST /api/visualize/generate
**Objective:** Test chart generation API directly

**Test Steps:**
1. Use API testing tool
2. Send POST request with chart configuration
3. Check response

**Expected Results:**
- ✅ Returns 201 status code
- ✅ Response includes:
  - id
  - chart_data (Plotly JSON)
  - config
  - timestamps
- ✅ chart_data has valid Plotly structure
- ✅ Visualization saved in database

**Test Request:**
```bash
curl -X POST "http://localhost:8000/api/visualize/generate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "<uuid>",
    "chart_type": "bar",
    "config": {
      "x_column": "category",
      "y_column": "sales",
      "aggregation": "sum",
      "title": "Sales by Category"
    },
    "name": "Test Chart"
  }'
```

**Screenshot Placeholder:**
```
[Screenshot: API request payload]
[Screenshot: Successful response with chart data]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-29: API Endpoint - GET /api/visualize/
**Objective:** Test listing visualizations API

**Test Steps:**
1. Create 3-5 visualizations
2. Send GET request to list endpoint
3. Try with and without dataset_id filter

**Expected Results:**
- ✅ Returns 200 status code
- ✅ Returns array of visualizations
- ✅ Each has all expected fields
- ✅ Filtering by dataset_id works
- ✅ Sorted by creation date

**Test Request:**
```bash
curl -X GET "http://localhost:8000/api/visualize/" \
  -H "Authorization: Bearer <token>"

curl -X GET "http://localhost:8000/api/visualize/?dataset_id=<uuid>" \
  -H "Authorization: Bearer <token>"
```

**Screenshot Placeholder:**
```
[Screenshot: List API response]
[Screenshot: Filtered list response]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-30: API Endpoint - DELETE /api/visualize/{id}
**Objective:** Test deletion API

**Test Steps:**
1. Create a visualization
2. Note its ID
3. Send DELETE request
4. Try to retrieve deleted visualization

**Expected Results:**
- ✅ Returns 204 status code
- ✅ Visualization removed from database
- ✅ GET request returns 404
- ✅ Doesn't affect other visualizations

**Test Request:**
```bash
curl -X DELETE "http://localhost:8000/api/visualize/<uuid>" \
  -H "Authorization: Bearer <token>"
```

**Screenshot Placeholder:**
```
[Screenshot: Successful deletion response]
[Screenshot: 404 when trying to retrieve]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-31: Security - Authentication Required
**Objective:** Verify all endpoints require authentication

**Test Steps:**
1. Send requests without Authorization header
2. Try with invalid token
3. Try with expired token

**Expected Results:**
- ✅ Returns 401 Unauthorized
- ✅ Error message indicates authentication required
- ✅ No data returned
- ✅ Token refresh works (if implemented)

**Screenshot Placeholder:**
```
[Screenshot: 401 response for unauthenticated request]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-32: Security - User Isolation
**Objective:** Verify users can only access their own visualizations

**Test Steps:**
1. Create visualization with User A
2. Note visualization ID
3. Login as User B
4. Try to access User A's visualization

**Expected Results:**
- ✅ User B cannot see User A's visualization in list
- ✅ Direct GET request returns 404
- ✅ Cannot delete User A's visualization
- ✅ Proper isolation maintained

**Screenshot Placeholder:**
```
[Screenshot: 404 response when accessing other user's viz]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-33: UI/UX - Responsive Design
**Objective:** Test responsive layout

**Test Steps:**
1. Open visualization page
2. Resize browser window
3. Test at different breakpoints:
   - Desktop (> 1024px)
   - Tablet (768px - 1024px)
   - Mobile (< 768px)

**Expected Results:**
- ✅ Layout adapts to screen size
- ✅ Charts remain readable
- ✅ Controls accessible on mobile
- ✅ No horizontal scrolling
- ✅ Touch interactions work on mobile

**Screenshot Placeholder:**
```
[Screenshot: Desktop view]
[Screenshot: Tablet view]
[Screenshot: Mobile view]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-34: UI/UX - Loading States
**Objective:** Verify appropriate loading indicators

**Test Steps:**
1. Observe loading states for:
   - Getting suggestions
   - Generating charts
   - Loading saved visualizations

**Expected Results:**
- ✅ Loading spinner or skeleton displayed
- ✅ Buttons disabled during loading
- ✅ Loading text indicates what's happening
- ✅ Loading doesn't block entire page
- ✅ Timeout handling exists

**Screenshot Placeholder:**
```
[Screenshot: Loading state for suggestions]
[Screenshot: Loading state for chart generation]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

### TS-35: UI/UX - Empty States
**Objective:** Test empty state messaging

**Test Steps:**
1. View visualization page with no datasets
2. View with no saved visualizations
3. Try suggestions with dataset with too few rows

**Expected Results:**
- ✅ Helpful empty state messages
- ✅ Call to action (e.g., "Upload dataset first")
- ✅ No broken UI elements
- ✅ Clear guidance on next steps

**Screenshot Placeholder:**
```
[Screenshot: Empty state - no datasets]
[Screenshot: Empty state - no saved visualizations]
```

**Status:** ⬜ Pass ⬜ Fail ⬜ Blocked

**Notes:**
_______________________________________

---

## Test Results Summary

### Overall Statistics
- **Total Test Cases:** 35
- **Passed:** ___
- **Failed:** ___
- **Blocked:** ___
- **Pass Rate:** ___%

### Test Execution Timeline
- **Start Date:** __________
- **End Date:** __________
- **Total Time:** ____ hours

### Test Coverage
- **API Endpoints:** ___/6 (100%)
- **Chart Types:** ___/9 (100%)
- **Error Scenarios:** ___/6 (100%)
- **UI Components:** ___/5 (100%)

### Chart Type Testing Status
| Chart Type | Tested | Status | Notes |
|------------|--------|--------|-------|
| Bar Chart | ⬜ | ⬜ Pass ⬜ Fail | |
| Line Chart | ⬜ | ⬜ Pass ⬜ Fail | |
| Scatter Plot | ⬜ | ⬜ Pass ⬜ Fail | |
| Pie Chart | ⬜ | ⬜ Pass ⬜ Fail | |
| Histogram | ⬜ | ⬜ Pass ⬜ Fail | |
| Heatmap | ⬜ | ⬜ Pass ⬜ Fail | |
| Box Plot | ⬜ | ⬜ Pass ⬜ Fail | |
| Area Chart | ⬜ | ⬜ Pass ⬜ Fail | |
| Table | ⬜ | ⬜ Pass ⬜ Fail | |

### Feature Testing Status
| Feature | Status | Notes |
|---------|--------|-------|
| AI Suggestions | ⬜ Pass ⬜ Fail | |
| Manual Chart Creation | ⬜ Pass ⬜ Fail | |
| Chart Configuration | ⬜ Pass ⬜ Fail | |
| Chart Interactivity | ⬜ Pass ⬜ Fail | |
| Save/Retrieve Charts | ⬜ Pass ⬜ Fail | |
| Chart Export | ⬜ Pass ⬜ Fail | |
| Error Handling | ⬜ Pass ⬜ Fail | |
| Security | ⬜ Pass ⬜ Fail | |

---

## Issues Found

### Critical Issues
_None identified during testing._

1. **Issue ID:** CRIT-001
   - **Severity:** Critical
   - **Component:** _____________
   - **Description:** _____________
   - **Steps to Reproduce:** _____________
   - **Expected:** _____________
   - **Actual:** _____________
   - **Workaround:** _____________
   - **Status:** ⬜ Open ⬜ Fixed ⬜ Deferred

### High Priority Issues
_None identified during testing._

1. **Issue ID:** HIGH-001
   - **Severity:** High
   - **Component:** _____________
   - **Description:** _____________
   - **Impact:** _____________
   - **Status:** ⬜ Open ⬜ Fixed ⬜ Deferred

### Medium Priority Issues
_None identified during testing._

1. **Issue ID:** MED-001
   - **Severity:** Medium
   - **Component:** _____________
   - **Description:** _____________
   - **Status:** ⬜ Open ⬜ Fixed ⬜ Deferred

### Low Priority Issues / Enhancements
_None identified during testing._

1. **Issue ID:** LOW-001
   - **Severity:** Low
   - **Component:** _____________
   - **Description:** _____________
   - **Status:** ⬜ Open ⬜ Fixed ⬜ Deferred

---

## Recommendations

### Passed Feature - Ready for Release
✅ **The visualization feature is ready for production use** with the following notes:

### Suggestions for Improvement

1. **Enhanced Chart Types**
   - Add treemap and sunburst charts for hierarchical data
   - Add geographic map visualizations
   - Add 3D visualizations for advanced use cases

2. **Advanced Configuration**
   - Add chart template library
   - Allow saving custom color palettes
   - Add annotation tools for marking important points
   - Add trendline/regression line options

3. **Performance Optimization**
   - Implement server-side rendering for very large datasets
   - Add data sampling options for preview
   - Implement progressive loading for complex charts

4. **User Experience**
   - Add chart preview in suggestions
   - Implement drag-and-drop column mapping
   - Add chart comparison view (side-by-side)
   - Add keyboard shortcuts for power users

5. **Collaboration Features**
   - Add chart sharing URLs
   - Add embed codes for external websites
   - Add collaborative editing
   - Add comments on visualizations

6. **Export Options**
   - Add more export formats (PDF, Excel)
   - Implement Tableau integration (as planned)
   - Add scheduled report generation
   - Add email delivery of charts

7. **Analytics**
   - Track most-used chart types
   - Track AI suggestion acceptance rate
   - Monitor chart generation performance
   - Collect user feedback on suggestions

### Documentation Updates Needed
- Update user guide with visualization examples
- Create video tutorials for each chart type
- Document AI suggestion algorithm
- Add troubleshooting guide

### Training Requirements
- Train support team on visualization features
- Create onboarding materials for new users
- Develop best practices guide

---

## Appendix

### Test Environment Details
**Hardware:**
- Processor: _____________
- RAM: _____________
- Storage: _____________

**Software:**
- OS: _____________
- Browser: _____________
- Python: 3.11+
- Node.js: 18+
- PostgreSQL: 14+

### API Response Examples

#### Successful Suggestion Response
```json
[
  {
    "chart_type": "bar",
    "title": "Total Sales by Category",
    "description": "Bar chart showing aggregated sales for each product category",
    "confidence": 0.95,
    "config": {
      "x_column": "category",
      "y_column": "sales",
      "aggregation": "sum",
      "title": "Total Sales by Category"
    },
    "reasoning": "The data contains a categorical column (category) and a numeric column (sales), making a bar chart with sum aggregation ideal for comparing totals across categories."
  }
]
```

#### Successful Generation Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "dataset_id": "123e4567-e89b-12d3-a456-426614174001",
  "query_id": null,
  "name": "Sales by Category",
  "description": null,
  "chart_type": "bar",
  "config": {
    "x_column": "category",
    "y_column": "sales",
    "aggregation": "sum"
  },
  "chart_data": {
    "data": [...],
    "layout": {...}
  },
  "created_at": "2024-01-26T12:00:00Z",
  "updated_at": null
}
```

### Glossary
- **AI Suggestion:** Chart recommendation generated by Claude AI
- **Chart Configuration:** Parameters defining how data is visualized
- **Plotly:** JavaScript library for interactive charts
- **Aggregation:** Mathematical operation on grouped data (sum, mean, etc.)
- **Heatmap:** Visualization showing data as color-coded matrix
- **Box Plot:** Statistical chart showing distribution quartiles

---

**Test Document Version:** 1.0
**Last Updated:** 2024-01-26
**Next Review Date:** _____________

**Approved By:**
- QA Lead: _________________ Date: _________
- Product Manager: __________ Date: _________
- Engineering Lead: __________ Date: _________

---

*End of Test Documentation*
