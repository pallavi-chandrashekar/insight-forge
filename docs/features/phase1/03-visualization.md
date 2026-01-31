# Visualization Feature Documentation

## Overview

The InsightForge visualization feature provides powerful, AI-driven data visualization capabilities that enable users to create interactive charts from their datasets with minimal configuration. The feature leverages Plotly for rich, interactive visualizations and Claude AI for intelligent chart recommendations.

## Key Features

### 1. Multiple Chart Types
Support for 9 different chart types to cover various data visualization needs:
- **Bar Chart**: Compare categorical data
- **Line Chart**: Show trends over time or continuous data
- **Scatter Plot**: Display relationships between two numeric variables
- **Pie Chart**: Show proportions and percentages
- **Histogram**: Visualize distribution of numeric data
- **Heatmap**: Display correlation matrices or pivot tables
- **Box Plot**: Show statistical distribution and outliers
- **Area Chart**: Emphasize magnitude of change over time
- **Table**: Structured data display

### 2. AI-Powered Visualization Suggestions
Claude AI analyzes dataset schema and sample data to recommend the most appropriate visualizations:
- Considers data types (numeric, categorical, datetime)
- Evaluates column relationships
- Suggests optimal chart configurations
- Provides confidence scores for each suggestion
- Explains reasoning behind recommendations

### 3. Interactive Configuration
Flexible chart configuration options:
- **x_column**: Primary x-axis column
- **y_column**: Primary y-axis column
- **color_column**: Grouping/coloring dimension
- **size_column**: Size dimension for scatter plots
- **aggregation**: Data aggregation method (sum, mean, count, etc.)
- **title**: Custom chart title
- **x_label/y_label**: Custom axis labels
- **values_column**: Values for heatmaps

### 4. Dataset and Query Integration
- Create visualizations from uploaded datasets
- Visualize query results directly
- Link visualizations to specific queries for reproducibility
- Auto-save visualization configurations

### 5. Visualization Management
- Save and retrieve visualizations
- List all user visualizations
- Filter by dataset
- Update visualization configurations
- Delete unwanted visualizations

## Architecture

### Backend Components

#### Models (`app/models/visualization.py`)
```python
class ChartType(Enum):
    BAR, LINE, SCATTER, PIE, HISTOGRAM, HEATMAP, BOX, AREA, TABLE

class Visualization:
    - id: UUID
    - user_id: UUID (foreign key)
    - dataset_id: UUID (foreign key)
    - query_id: UUID (optional, foreign key)
    - name: string
    - description: text
    - chart_type: ChartType
    - config: JSON
    - chart_data: JSON (Plotly chart specification)
    - created_at/updated_at: timestamps
```

#### Services (`app/services/visualization_service.py`)
- `create_plotly_chart()`: Generate Plotly charts from DataFrames
- `save_visualization()`: Persist visualization to database
- `get_visualization()`: Retrieve specific visualization
- `get_user_visualizations()`: List user's visualizations
- `delete_visualization()`: Remove visualization

#### LLM Service (`app/services/llm_service.py`)
- `suggest_visualizations()`: AI-powered chart recommendations
  - Analyzes schema and sample data
  - Returns 3-5 suggestions with confidence scores
  - Includes pre-configured chart parameters

### API Endpoints

#### POST `/api/visualize/generate`
Generate and save a new visualization.

**Request:**
```json
{
  "dataset_id": "uuid",
  "query_id": "uuid (optional)",
  "chart_type": "bar|line|scatter|pie|histogram|heatmap|box|area|table",
  "config": {
    "x_column": "column_name",
    "y_column": "column_name",
    "color_column": "column_name (optional)",
    "size_column": "column_name (optional)",
    "aggregation": "sum|mean|count|etc (optional)",
    "title": "Chart Title (optional)",
    "x_label": "X Axis Label (optional)",
    "y_label": "Y Axis Label (optional)"
  },
  "name": "Visualization Name (optional)",
  "description": "Description (optional)"
}
```

**Response:**
```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "query_id": "uuid or null",
  "name": "string or null",
  "description": "string or null",
  "chart_type": "bar",
  "config": {...},
  "chart_data": {...}, // Plotly JSON spec
  "created_at": "2024-01-26T12:00:00Z",
  "updated_at": "2024-01-26T12:00:00Z"
}
```

#### POST `/api/visualize/suggest`
Get AI-powered visualization suggestions for a dataset.

**Request:**
```json
{
  "dataset_id": "uuid"
}
```

**Response:**
```json
[
  {
    "chart_type": "bar",
    "title": "Sales by Product Category",
    "description": "Bar chart showing total sales for each product category",
    "confidence": 0.95,
    "config": {
      "x_column": "category",
      "y_column": "sales",
      "aggregation": "sum"
    },
    "reasoning": "The data contains a categorical column (category) and a numeric column (sales), making a bar chart ideal for comparing totals across categories."
  },
  ...
]
```

#### GET `/api/visualize/`
List all visualizations for the current user, optionally filtered by dataset.

**Query Parameters:**
- `dataset_id` (optional): Filter by dataset UUID

**Response:**
```json
[
  {
    "id": "uuid",
    "dataset_id": "uuid",
    "name": "Sales Dashboard",
    "chart_type": "bar",
    ...
  },
  ...
]
```

#### GET `/api/visualize/{viz_id}`
Retrieve a specific visualization by ID.

**Response:** Same as generate response

#### DELETE `/api/visualize/{viz_id}`
Delete a visualization.

**Response:** 204 No Content

## Data Flow

### Visualization Generation Flow
```
User Request (chart type + config)
         ↓
Load Dataset/Query Results
         ↓
Create DataFrame
         ↓
VisualizationService.create_plotly_chart()
         ↓
Generate Plotly JSON
         ↓
Save to Database
         ↓
Return Chart Data to Frontend
         ↓
Render with Plotly.js
```

### AI Suggestion Flow
```
User Request (dataset_id)
         ↓
Load Dataset Metadata
         ↓
Extract Schema + Sample Data
         ↓
LLMService.suggest_visualizations()
         ↓
Claude API Call
         ↓
Parse JSON Suggestions
         ↓
Return Recommendations to Frontend
         ↓
Display Suggestions with Preview
```

## Frontend Components (To Be Implemented)

### ChartContainer
- Renders Plotly charts
- Handles interactive features (zoom, pan, hover)
- Export capabilities (PNG, SVG, PDF)
- Responsive sizing

### VizSuggestions
- Displays AI-recommended charts
- Shows confidence scores
- Preview functionality
- One-click chart generation

### ChartSelector
- Grid of available chart types
- Visual icons for each type
- Description and use cases
- Data requirement indicators

### VizConfig
- Dynamic form based on chart type
- Column selectors with data type validation
- Aggregation options
- Styling controls

## Usage Examples

### Example 1: Generate Bar Chart
```python
import requests

# Generate a bar chart of sales by category
response = requests.post(
    "http://localhost:8000/api/visualize/generate",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "dataset_id": "dataset-uuid",
        "chart_type": "bar",
        "config": {
            "x_column": "category",
            "y_column": "sales",
            "aggregation": "sum",
            "title": "Total Sales by Category"
        },
        "name": "Sales Overview"
    }
)

chart_data = response.json()["chart_data"]
```

### Example 2: Get AI Suggestions
```python
# Get AI-powered chart recommendations
response = requests.post(
    "http://localhost:8000/api/visualize/suggest",
    headers={"Authorization": f"Bearer {token}"},
    params={"dataset_id": "dataset-uuid"}
)

suggestions = response.json()
for suggestion in suggestions:
    print(f"{suggestion['title']} (confidence: {suggestion['confidence']})")
    print(f"  Type: {suggestion['chart_type']}")
    print(f"  Reasoning: {suggestion['reasoning']}")
```

### Example 3: Visualize Query Results
```python
# Execute a query first
query_response = requests.post(
    "http://localhost:8000/api/query/execute",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "dataset_id": "dataset-uuid",
        "query": "SELECT category, SUM(sales) as total FROM df GROUP BY category",
        "query_type": "sql"
    }
)
query_id = query_response.json()["id"]

# Create visualization from query results
viz_response = requests.post(
    "http://localhost:8000/api/visualize/generate",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "dataset_id": "dataset-uuid",
        "query_id": query_id,
        "chart_type": "bar",
        "config": {
            "x_column": "category",
            "y_column": "total",
            "title": "Sales by Category"
        }
    }
)
```

## Chart Type Reference

### Bar Chart
- **Best for**: Comparing values across categories
- **Required**: x_column (categorical), y_column (numeric)
- **Optional**: color_column, aggregation
- **Example**: Sales by product, counts by region

### Line Chart
- **Best for**: Trends over time or continuous data
- **Required**: x_column (datetime/numeric), y_column (numeric)
- **Optional**: color_column (multiple lines)
- **Example**: Revenue over months, temperature trends

### Scatter Plot
- **Best for**: Relationships between numeric variables
- **Required**: x_column (numeric), y_column (numeric)
- **Optional**: color_column, size_column
- **Example**: Price vs. quantity, correlation analysis

### Pie Chart
- **Best for**: Part-to-whole relationships
- **Required**: x_column (categorical), y_column (numeric)
- **Optional**: aggregation
- **Example**: Market share, budget allocation

### Histogram
- **Best for**: Distribution of numeric data
- **Required**: x_column (numeric)
- **Optional**: color_column, bins
- **Example**: Age distribution, score frequency

### Heatmap
- **Best for**: Correlation matrices, pivot tables
- **Required**: Either correlation matrix or x_column + y_column + values_column
- **Optional**: aggregation
- **Example**: Correlation matrix, sales by region and product

### Box Plot
- **Best for**: Statistical distribution, outliers
- **Required**: y_column (numeric)
- **Optional**: x_column (categorical grouping), color_column
- **Example**: Salary distribution by department

### Area Chart
- **Best for**: Cumulative trends over time
- **Required**: x_column (datetime/numeric), y_column (numeric)
- **Optional**: color_column (stacked areas)
- **Example**: Cumulative sales, stacked categories over time

## Error Handling

### Common Errors
1. **Dataset not found (404)**: Invalid dataset_id
2. **Query not found (404)**: Invalid query_id
3. **No query results (400)**: Query has no results to visualize
4. **Invalid chart configuration (400)**: Missing required columns or invalid aggregation
5. **Data loading error (500)**: File corrupted or missing
6. **Chart generation error (500)**: Invalid data types for chart type

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## Performance Considerations

1. **Large Datasets**: Charts are generated from sampled data for datasets > 10,000 rows
2. **Caching**: Visualization suggestions are cached for 1 hour per dataset
3. **Async Processing**: Chart generation runs asynchronously for large datasets
4. **Plotly Optimization**: Use WebGL for scatter plots with > 1,000 points

## Security

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access their own visualizations
3. **Data Isolation**: Visualizations are user-scoped via foreign keys
4. **Input Validation**: Pydantic schemas validate all requests

## Testing

### Unit Tests
- Test each chart type generation
- Test AI suggestion parsing
- Test configuration validation
- Test error handling

### Integration Tests
- Test full visualization flow
- Test with different datasets
- Test query result visualization
- Test API endpoints

### E2E Tests
- Test frontend chart rendering
- Test user interactions
- Test chart export
- Test suggestion acceptance

## Future Enhancements

1. **Additional Chart Types**
   - Treemap, Sunburst, Sankey diagrams
   - 3D scatter and surface plots
   - Geographic maps

2. **Advanced Features**
   - Chart templates
   - Dashboard creation
   - Scheduled report generation
   - Real-time data updates

3. **Customization**
   - Theme editor
   - Custom color palettes
   - Font and styling options
   - Annotation tools

4. **Sharing**
   - Public chart links
   - Embed codes
   - Collaborative editing
   - Comments and feedback

5. **Export Options**
   - Tableau integration (planned)
   - Power BI export
   - Static image export (PNG, SVG, PDF)
   - Data export (CSV, JSON)

## Dependencies

### Backend
- `plotly>=5.24.0`: Chart generation
- `pandas>=2.2.0`: Data manipulation
- `anthropic`: Claude AI integration

### Frontend (To Be Added)
- `plotly.js` or `react-plotly.js`: Chart rendering
- Chart component library

## Configuration

Environment variables in `.env`:
```
API_KEY=your_anthropic_api_key
LLM_MODEL=claude-sonnet-4-5-20250929
LLM_MAX_TOKENS=4096
```

## Support

For issues or questions:
- Check logs at `/var/log/insightforge/`
- API documentation at `http://localhost:8000/docs`
- GitHub issues: [project-url]/issues
