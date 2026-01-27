# Feature: Visualization & Chart Generation

## Overview
Enable users to create interactive visualizations from their datasets and query results, with AI-powered chart suggestions based on data characteristics.

## Status
🚧 **TO BE IMPLEMENTED**

## Dependencies
- ✅ Feature 01: Data Upload & Management (for datasets)
- 🚧 Feature 02: Query Execution (for query results)

---

## User Stories

### US-1: AI-Powered Chart Suggestions
**As a** data analyst
**I want to** get AI-powered visualization suggestions
**So that** I can quickly find the best way to visualize my data

**Acceptance Criteria:**
- [ ] Analyze dataset schema and sample data
- [ ] Use Claude AI to suggest appropriate chart types
- [ ] Rank suggestions by confidence score
- [ ] Provide reasoning for each suggestion
- [ ] Support 3-5 suggestions per dataset
- [ ] Suggest based on:
  - Column data types (numeric, categorical, datetime)
  - Number of unique values
  - Relationships between columns
  - Statistical properties
- [ ] Display suggestions with preview thumbnails
- [ ] One-click chart generation from suggestions

### US-2: Manual Chart Creation
**As a** user
**I want to** manually create visualizations
**So that** I can customize exactly what I want to see

**Acceptance Criteria:**
- [ ] Chart type selector (bar, line, scatter, pie, histogram, heatmap, box, area, table)
- [ ] Column mapping interface:
  - X-axis column selector
  - Y-axis column selector
  - Color/group by selector
  - Size column (for scatter plots)
  - Filter options
- [ ] Aggregation options (sum, mean, count, min, max)
- [ ] Chart customization:
  - Title and labels
  - Color scheme
  - Legend position
  - Axis ranges
- [ ] Live preview as configuration changes
- [ ] Save chart configuration

### US-3: Interactive Charts
**As a** user
**I want** interactive charts
**So that** I can explore data dynamically

**Acceptance Criteria:**
- [ ] Hover tooltips showing data values
- [ ] Zoom and pan functionality
- [ ] Click to filter/drill-down (future)
- [ ] Legend toggle (show/hide series)
- [ ] Responsive to window resize
- [ ] Download chart as PNG/SVG/JSON
- [ ] Full-screen mode

### US-4: Visualization from Query Results
**As a** user
**I want to** visualize query results directly
**So that** I can see the output of my queries as charts

**Acceptance Criteria:**
- [ ] "Visualize" button on query results
- [ ] Carry over query context
- [ ] Auto-suggest charts based on result schema
- [ ] Link visualization to source query
- [ ] Re-run query when viewing saved visualization

### US-5: Visualization Library
**As a** user
**I want to** manage my saved visualizations
**So that** I can reuse and organize my charts

**Acceptance Criteria:**
- [ ] List all saved visualizations
- [ ] Display thumbnail previews
- [ ] Show metadata (name, dataset, chart type, date)
- [ ] Search and filter visualizations
- [ ] Edit visualization configuration
- [ ] Duplicate visualizations
- [ ] Delete visualizations
- [ ] Export visualization

### US-6: Tableau Integration (Optional)
**As a** enterprise user
**I want to** export to Tableau
**So that** I can use advanced Tableau features

**Acceptance Criteria:**
- [ ] Configure Tableau credentials in profile
- [ ] Export dataset to Tableau Server
- [ ] Generate Tableau workbook
- [ ] Return Tableau workbook URL
- [ ] Fallback to Plotly if not configured

---

## API Endpoints

### 1. Get Chart Suggestions
```http
POST /api/visualize/suggest
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "dataset_id": "uuid",
  "query_id": "uuid", // Optional - for query result viz
  "context": "I want to analyze sales trends over time"
}

Response: 200 OK
[
  {
    "chart_type": "line",
    "title": "Sales Trend Over Time",
    "description": "Shows how sales change over the time period",
    "confidence": 0.95,
    "reasoning": "Dataset contains a datetime column and a numeric sales column, making a line chart ideal for trend analysis",
    "config": {
      "x_column": "date",
      "y_column": "sales",
      "aggregation": "sum",
      "color_column": null
    }
  },
  {
    "chart_type": "bar",
    "title": "Sales by Category",
    "description": "Compares sales across different categories",
    "confidence": 0.88,
    "config": {
      "x_column": "category",
      "y_column": "sales",
      "aggregation": "sum",
      "color_column": "region"
    }
  },
  ...
]
```

### 2. Generate Visualization
```http
POST /api/visualize/generate
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "dataset_id": "uuid",
  "query_id": "uuid", // Optional
  "name": "Sales by Region",
  "description": "Monthly sales broken down by region",
  "chart_type": "bar",
  "config": {
    "x_column": "region",
    "y_column": "sales",
    "aggregation": "sum",
    "color_column": "product_category",
    "title": "Sales by Region",
    "x_label": "Region",
    "y_label": "Total Sales ($)",
    "color_scheme": "viridis"
  }
}

Response: 201 Created
{
  "id": "viz-uuid",
  "name": "Sales by Region",
  "chart_type": "bar",
  "chart_data": {
    // Plotly JSON specification
    "data": [...],
    "layout": {...}
  },
  "image_path": "/visualizations/user-id/viz-uuid.png",
  "created_at": "2024-01-25T10:00:00Z"
}
```

### 3. List Visualizations
```http
GET /api/visualize?dataset_id=uuid&skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "Sales by Region",
    "chart_type": "bar",
    "dataset_id": "uuid",
    "dataset_name": "Sales Data",
    "thumbnail_url": "/thumbnails/uuid.png",
    "created_at": "2024-01-25T10:00:00Z"
  },
  ...
]
```

### 4. Get Visualization Details
```http
GET /api/visualize/{id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "name": "Sales by Region",
  "description": "Monthly sales broken down by region",
  "chart_type": "bar",
  "config": {...},
  "chart_data": {
    // Full Plotly specification
  },
  "dataset_id": "uuid",
  "query_id": "uuid",
  "created_at": "2024-01-25T10:00:00Z"
}
```

### 5. Update Visualization
```http
PUT /api/visualize/{id}
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "name": "Updated Name",
  "config": {...}
}

Response: 200 OK
{
  // Updated visualization
}
```

### 6. Delete Visualization
```http
DELETE /api/visualize/{id}
Authorization: Bearer <token>

Response: 204 No Content
```

### 7. Export to Tableau (Optional)
```http
POST /api/visualize/{id}/tableau-export
Authorization: Bearer <token>

Response: 200 OK
{
  "workbook_url": "https://tableau.server.com/workbooks/123",
  "success": true
}
```

---

## Technical Implementation

### Backend Components

#### VisualizationService (`backend/app/services/visualization_service.py`)

**Methods:**

```python
class VisualizationService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def suggest_charts(
        self,
        dataset_id: str,
        schema: dict,
        sample_data: List[dict],
        context: str = None
    ) -> List[ChartSuggestion]:
        """Get AI-powered chart suggestions"""
        # Analyze schema
        column_types = self._analyze_column_types(schema)

        # Call LLM for suggestions
        suggestions = await self.llm_service.suggest_visualizations(
            schema=schema,
            sample_data=sample_data,
            context=context
        )

        # Rank by confidence
        # Add reasoning
        # Return top 3-5 suggestions

    async def generate_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        config: dict
    ) -> dict:
        """Generate Plotly chart from configuration"""
        # Extract columns from config
        x_col = config.get("x_column")
        y_col = config.get("y_column")
        color_col = config.get("color_column")

        # Apply aggregation if specified
        if config.get("aggregation"):
            df = self._apply_aggregation(df, config)

        # Generate chart based on type
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col)
        elif chart_type == "heatmap":
            fig = px.imshow(df.corr())
        elif chart_type == "box":
            fig = px.box(df, x=x_col, y=y_col)
        elif chart_type == "area":
            fig = px.area(df, x=x_col, y=y_col)

        # Apply customizations
        fig.update_layout(
            title=config.get("title"),
            xaxis_title=config.get("x_label"),
            yaxis_title=config.get("y_label")
        )

        # Return Plotly JSON
        return fig.to_json()

    async def export_to_tableau(
        self,
        df: pd.DataFrame,
        credentials: dict
    ) -> str:
        """Export to Tableau Server (optional)"""
        # Connect to Tableau Server
        # Upload dataset
        # Create workbook
        # Return workbook URL

    def _analyze_column_types(self, schema: dict) -> dict:
        """Categorize columns by type"""
        numeric_cols = []
        categorical_cols = []
        datetime_cols = []

        for col in schema["columns"]:
            dtype = col["dtype"]
            if "int" in dtype or "float" in dtype:
                numeric_cols.append(col["name"])
            elif "datetime" in dtype:
                datetime_cols.append(col["name"])
            else:
                categorical_cols.append(col["name"])

        return {
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "datetime": datetime_cols
        }

    def _apply_aggregation(
        self,
        df: pd.DataFrame,
        config: dict
    ) -> pd.DataFrame:
        """Apply aggregation to data"""
        group_by = config.get("x_column")
        agg_col = config.get("y_column")
        agg_func = config.get("aggregation", "sum")

        return df.groupby(group_by)[agg_col].agg(agg_func).reset_index()
```

#### LLMService Enhancement

**New Method:**
```python
async def suggest_visualizations(
    self,
    schema: dict,
    sample_data: List[dict],
    context: str = None
) -> List[dict]:
    """Use Claude to suggest appropriate visualizations"""

    system_prompt = """You are a data visualization expert.
    Analyze the data schema and suggest appropriate visualizations.

    Return JSON array with:
    - chart_type: one of "bar", "line", "scatter", "pie", "histogram", "heatmap", "box", "area"
    - title: descriptive title
    - description: what this shows
    - confidence: 0-1 score
    - config: {x_column, y_column, color_column, aggregation}
    - reasoning: why this is appropriate

    Consider:
    - Data types (numeric, categorical, datetime)
    - Number of unique values
    - Relationships between columns
    - Best practices for visualization

    Return 3-5 suggestions ordered by confidence."""

    user_prompt = f"""Schema: {schema}
    Sample data: {sample_data}
    Context: {context or 'General analysis'}

    Suggest visualizations:"""

    response = await self._call_claude(system_prompt, user_prompt)
    return json.loads(response)
```

#### Visualization Routes (`backend/app/api/routes/visualize.py`)

**Dependencies:**
- Current user (JWT)
- VisualizationService
- DataService (load datasets)
- QueryEngine (if visualizing query results)
- Database session

### Frontend Components

#### Visualize Page (`frontend/src/pages/Visualize.tsx`)

**State:**
- Selected dataset/query
- Suggested charts
- Selected chart type
- Chart configuration
- Chart data (Plotly JSON)
- Loading state

**Components:**
- Dataset/Query selector
- Suggestions carousel
  - Chart preview cards
  - Confidence scores
  - "Use this" button
- Chart type selector (manual)
- Configuration panel
  - Column selectors
  - Aggregation dropdown
  - Customization options (title, labels, colors)
- Live preview area (react-plotly.js)
- Action buttons
  - Save
  - Export (PNG, SVG, JSON)
  - Share (future)

#### Chart Suggestions Component

**Props:**
- Dataset ID
- Query ID (optional)
- onSelect callback

**Features:**
- Fetch suggestions from API
- Display as cards with preview
- Show confidence and reasoning
- Click to apply suggestion

#### Chart Configuration Panel

**Props:**
- Chart type
- Available columns
- Current config
- onChange callback

**Components:**
- X-axis column selector
- Y-axis column selector
- Group/color selector
- Aggregation dropdown
- Title input
- Axis label inputs
- Color scheme selector

#### Plotly Chart Component

**Props:**
- Chart data (Plotly JSON)
- Config options

**Features:**
- Render interactive chart
- Responsive sizing
- Export buttons
- Full-screen mode

### Database Schema

```sql
CREATE TYPE charttype AS ENUM (
    'bar', 'line', 'scatter', 'pie',
    'histogram', 'heatmap', 'box', 'area', 'table'
);

CREATE TABLE visualizations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    query_id UUID REFERENCES queries(id) ON DELETE SET NULL,
    name VARCHAR(255),
    description TEXT,
    chart_type charttype NOT NULL,
    config JSONB NOT NULL, -- Chart configuration
    chart_data JSONB, -- Plotly JSON
    image_path VARCHAR(512), -- Static image for thumbnail
    tableau_workbook_url VARCHAR(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_visualizations_user_id ON visualizations(user_id);
CREATE INDEX idx_visualizations_dataset_id ON visualizations(dataset_id);
CREATE INDEX idx_visualizations_created_at ON visualizations(created_at DESC);
```

---

## Chart Type Guidelines

### Bar Chart
**Best for:** Comparing categorical data
**Requirements:**
- X: Categorical column
- Y: Numeric column
- Optional: Color by another categorical

### Line Chart
**Best for:** Time series and trends
**Requirements:**
- X: Datetime or ordered numeric
- Y: Numeric column
- Optional: Multiple lines for comparison

### Scatter Plot
**Best for:** Relationships between two numeric variables
**Requirements:**
- X: Numeric column
- Y: Numeric column
- Optional: Color and size dimensions

### Pie Chart
**Best for:** Part-to-whole relationships
**Requirements:**
- Names: Categorical column
- Values: Numeric column
- Limit: < 7 categories recommended

### Histogram
**Best for:** Distribution of numeric data
**Requirements:**
- X: Numeric column
- Bins: Auto or specified

### Heatmap
**Best for:** Correlation or density
**Requirements:**
- Multiple numeric columns
- Shows correlation matrix or pivot table

### Box Plot
**Best for:** Distribution and outliers
**Requirements:**
- Y: Numeric column
- Optional X: Categorical for grouping

### Area Chart
**Best for:** Cumulative trends over time
**Requirements:**
- X: Datetime or ordered
- Y: Numeric column

---

## Integration with Other Features

### With Data Upload (Feature 01)
- Load dataset for visualization
- Access schema for column selection
- Use sample data for suggestions

### With Query Execution (Feature 02)
- Visualize query results directly
- "Visualize" button on query page
- Link visualization to source query
- Re-run query when viewing viz

**Flow:**
```
User executes query → Gets results
         │
         ▼
    Click "Visualize" button
         │
         ▼
    Navigate to Visualize page with query context
         │
         ▼
    Get AI suggestions based on result schema
         │
         ▼
    User selects or configures chart
         │
         ▼
    Generate and display chart
         │
         ▼
    Save visualization (linked to query)
```

---

## Security Considerations

1. **Data Access**
   - Users can only visualize their own datasets
   - Query results are user-scoped
   - Visualization access controlled

2. **Resource Limits**
   - Limit data points in charts (max 10,000)
   - Sample large datasets for preview
   - Timeout for chart generation

3. **Tableau Integration**
   - Encrypt stored credentials
   - Use secure connections (HTTPS)
   - Validate Tableau server certificates

---

## Performance Optimizations

1. **Chart Generation**
   - Sample large datasets (> 100k rows)
   - Aggregate data before plotting
   - Cache chart data

2. **LLM Suggestions**
   - Cache suggestions for same dataset
   - Use schema only (not full data)
   - Parallel suggestion generation

3. **Image Export**
   - Generate thumbnails asynchronously
   - Store static images for gallery
   - CDN for image delivery

**Benchmarks (Target):**
- Suggestions generation: < 3 seconds
- Chart rendering: < 500ms
- Image export: < 2 seconds

---

## Testing Strategy

### Unit Tests
- [ ] Chart configuration validation
- [ ] Plotly JSON generation
- [ ] Column type analysis
- [ ] Aggregation logic

### Integration Tests
- [ ] End-to-end visualization flow
- [ ] AI suggestions accuracy
- [ ] Chart rendering
- [ ] Export functionality

### Visual Regression Tests
- [ ] Chart appearance consistency
- [ ] Responsive layouts
- [ ] Theme support

---

## Dependencies

**Backend:**
- plotly >= 5.24.1 (Chart generation)
- kaleido >= 0.2.1 (Static image export)
- matplotlib >= 3.9.3 (Fallback charts)
- anthropic >= 0.39.0 (AI suggestions)

**Frontend:**
- react-plotly.js >= 2.6.0 (Chart rendering)
- plotly.js >= 2.27.0 (Plotly library)

---

## Future Enhancements

1. **Advanced Charts**
   - Sankey diagrams
   - Network graphs
   - 3D visualizations
   - Geographic maps

2. **Dashboard Builder**
   - Multiple charts per page
   - Drag-and-drop layout
   - Shared filters
   - Refresh schedules

3. **Annotations**
   - Add text annotations
   - Draw shapes
   - Highlight regions
   - Add reference lines

4. **Animations**
   - Time-based animations
   - Transition effects
   - Play/pause controls

5. **Collaboration**
   - Share visualizations
   - Comments on charts
   - Version history
   - Embed in other apps

---

## Success Metrics

- Chart generation success rate > 95%
- AI suggestion accuracy > 85%
- Average time to create chart < 2 minutes
- User satisfaction rating > 4.5/5
- Visualizations created per user per week

---

## Documentation

- [ ] API documentation (Swagger)
- [ ] User guide with examples
- [ ] Chart type guide
- [ ] Best practices guide
- [ ] Plotly customization reference
- [ ] This feature spec
