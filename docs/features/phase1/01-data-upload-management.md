# Feature: Data Upload & Dataset Management

## Overview
Enable users to import data from multiple sources (file upload, URL, web scraping) and manage their datasets within the platform.

## Status
🚧 **TO BE IMPLEMENTED**

---

## User Stories

### US-1: File Upload
**As a** data analyst
**I want to** upload CSV, JSON, Excel, or Parquet files
**So that** I can analyze my local datasets in the platform

**Acceptance Criteria:**
- [ ] Support CSV files
- [ ] Support JSON files (flat and nested)
- [ ] Support Excel files (.xlsx, .xls)
- [ ] Support Parquet files
- [ ] File size limit enforced (100MB default)
- [ ] File type validation
- [ ] Display upload progress
- [ ] Show success/error messages
- [ ] Automatic schema inference
- [ ] Store metadata in database

### US-2: URL Data Import
**As a** data analyst
**I want to** import data from a public URL
**So that** I can analyze remote datasets without downloading them first

**Acceptance Criteria:**
- [ ] Support CSV URLs
- [ ] Support JSON URLs
- [ ] Automatic format detection
- [ ] Handle authentication (basic auth, headers)
- [ ] Timeout handling
- [ ] Error messages for invalid URLs
- [ ] Preview before import

### US-3: Web Scraping
**As a** data analyst
**I want to** scrape HTML tables from web pages
**So that** I can extract and analyze data from websites

**Acceptance Criteria:**
- [ ] URL input
- [ ] Optional CSS selector for table targeting
- [ ] Automatic table detection
- [ ] HTML parsing with BeautifulSoup
- [ ] Extract headers and data rows
- [ ] Handle pagination (future enhancement)

### US-4: Dataset Listing
**As a** user
**I want to** see all my uploaded datasets
**So that** I can choose which one to analyze

**Acceptance Criteria:**
- [ ] List all user datasets
- [ ] Display dataset name, source type, row count, column count
- [ ] Display creation date
- [ ] Sort by date (newest first)
- [ ] Search/filter datasets (future)
- [ ] Pagination for large lists (future)

### US-5: Dataset Details & Preview
**As a** user
**I want to** view dataset details and preview the data
**So that** I can understand the structure before querying

**Acceptance Criteria:**
- [ ] Display dataset metadata (name, description, source, stats)
- [ ] Show schema (column names, types, nullable, sample values)
- [ ] Preview first 100 rows by default
- [ ] Configurable preview limit
- [ ] Column sorting in preview
- [ ] Data type indicators

### US-6: Dataset Deletion
**As a** user
**I want to** delete datasets I no longer need
**So that** I can manage my storage space

**Acceptance Criteria:**
- [ ] Delete button on dataset page
- [ ] Confirmation dialog
- [ ] Cascade delete (queries, visualizations)
- [ ] Remove physical files from storage
- [ ] Success confirmation message

---

## API Endpoints

### 1. Upload File
```http
POST /api/datasets/upload
Content-Type: multipart/form-data

Request:
- file: File (required)
- name: string (optional)
- description: string (optional)

Response: 201 Created
{
  "id": "uuid",
  "name": "Sales Data",
  "source_type": "file",
  "file_type": "csv",
  "row_count": 1000,
  "column_count": 5,
  "schema": { ... },
  "created_at": "2024-01-25T10:00:00Z"
}
```

### 2. Import from URL
```http
POST /api/datasets/from-url
Content-Type: application/json

Request:
{
  "url": "https://example.com/data.csv",
  "name": "Remote Dataset",
  "description": "Optional description",
  "auth_headers": { "Authorization": "Bearer token" }
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Remote Dataset",
  "source_type": "url",
  "source_url": "https://example.com/data.csv",
  ...
}
```

### 3. Scrape Web Table
```http
POST /api/datasets/scrape
Content-Type: application/json

Request:
{
  "url": "https://example.com/page",
  "name": "Scraped Table",
  "css_selector": "table.data-table",
  "description": "Optional"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Scraped Table",
  "source_type": "scrape",
  ...
}
```

### 4. List Datasets
```http
GET /api/datasets
Authorization: Bearer <token>

Query Parameters:
- skip: int (default: 0)
- limit: int (default: 100)

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "Dataset 1",
    "source_type": "file",
    ...
  },
  ...
]
```

### 5. Get Dataset Details
```http
GET /api/datasets/{id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "name": "Dataset Name",
  "schema": {
    "columns": [
      {
        "name": "id",
        "dtype": "int64",
        "nullable": false,
        "sample_values": [1, 2, 3]
      }
    ]
  },
  ...
}
```

### 6. Preview Dataset
```http
GET /api/datasets/{id}/preview?limit=100
Authorization: Bearer <token>

Response: 200 OK
{
  "columns": ["id", "name", "value"],
  "data": [
    [1, "Alice", 100],
    [2, "Bob", 200]
  ],
  "total_rows": 1000
}
```

### 7. Delete Dataset
```http
DELETE /api/datasets/{id}
Authorization: Bearer <token>

Response: 204 No Content
```

---

## Technical Implementation

### Backend Components

#### DataService (`backend/app/services/data_service.py`)

**Methods:**
- `parse_file(file: UploadFile) -> pd.DataFrame`
  - Detects file type by extension
  - Parses CSV, JSON, Excel, Parquet
  - Returns pandas DataFrame

- `fetch_from_url(url: str, headers: dict) -> pd.DataFrame`
  - Async HTTP request with aiohttp
  - Auto-detects format from content-type
  - Downloads and parses data

- `scrape_webpage(url: str, selector: str) -> pd.DataFrame`
  - Fetches HTML with requests
  - Parses with BeautifulSoup
  - Extracts table data

- `infer_schema(df: pd.DataFrame) -> dict`
  - Extracts column names
  - Detects data types (int, float, string, date)
  - Identifies nullable columns
  - Samples 5 values per column
  - Calculates row/column counts

- `save_dataset_file(df: pd.DataFrame, dataset_id: str) -> str`
  - Saves DataFrame as Parquet (efficient storage)
  - Returns file path

- `load_dataset(dataset_id: str) -> pd.DataFrame`
  - Loads DataFrame from file
  - Caches in memory (optional)

- `get_preview(df: pd.DataFrame, limit: int) -> dict`
  - Returns first N rows
  - Converts to JSON-serializable format

#### Dataset Routes (`backend/app/api/routes/datasets.py`)

**Dependencies:**
- Current user from JWT
- DataService instance
- Database session

**Error Handling:**
- 400 Bad Request: Invalid file type, malformed data
- 404 Not Found: Dataset not found
- 413 Payload Too Large: File size exceeds limit
- 500 Internal Server Error: Processing failures

### Frontend Components

#### Upload Page (`frontend/src/pages/Upload.tsx`)

**State:**
- Upload mode (file, url, scrape)
- Form data
- Loading state
- Error messages

**Components:**
- Mode selector (tabs)
- File input with drag-and-drop
- URL input form
- Web scraping form
- Submit button
- Progress indicator
- Error display

#### Dataset Page (`frontend/src/pages/Dataset.tsx`)

**Props:**
- Dataset ID from route params

**State:**
- Dataset details
- Preview data
- Preview limit
- Loading state

**Components:**
- Metadata card
- Schema table
- Preview table with pagination
- Action buttons (delete, query, visualize)

### Database Schema

```sql
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) NOT NULL, -- 'file', 'url', 'scrape'
    source_url VARCHAR(1024),
    file_path VARCHAR(512),
    original_filename VARCHAR(255),
    file_size INTEGER,
    file_type VARCHAR(50),
    schema JSONB,
    row_count INTEGER,
    column_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_datasets_created_at ON datasets(created_at DESC);
```

---

## File Storage

**Location:** `./uploads/{user_id}/{dataset_id}.parquet`

**Format:** Parquet (compressed, efficient)

**Security:**
- User-isolated directories
- Unique filenames (UUID)
- File type validation
- Size limits enforced

---

## Testing

### Unit Tests
- [ ] File parsing (CSV, JSON, Excel, Parquet)
- [ ] Schema inference
- [ ] URL fetching
- [ ] Web scraping
- [ ] Error handling

### Integration Tests
- [ ] End-to-end upload flow
- [ ] URL import flow
- [ ] Web scraping flow
- [ ] Dataset CRUD operations

### Manual Testing
- [ ] Upload various file formats
- [ ] Import from public URLs
- [ ] Scrape web tables
- [ ] View dataset details
- [ ] Delete datasets

---

## Security Considerations

1. **File Upload**
   - Validate file extensions
   - Check MIME types
   - Scan for malware (future)
   - Size limits enforced

2. **URL Import**
   - Timeout limits (30 seconds)
   - Size limits (100MB)
   - No SSRF attacks (validate URLs)
   - Handle redirects safely

3. **Web Scraping**
   - Rate limiting
   - Respect robots.txt (future)
   - Timeout limits
   - No malicious scripts execution

4. **Data Storage**
   - User-isolated storage
   - Encrypted at rest (future)
   - Access control enforcement

---

## Performance

**Optimizations:**
- Async file processing
- Streaming for large files
- Parquet compression
- Schema caching
- Preview sampling (not full dataset)

**Benchmarks:**
- CSV 10MB: ~2 seconds
- Excel 5MB: ~3 seconds
- Parquet 20MB: ~1 second
- URL fetch: ~5 seconds (network dependent)

---

## Future Enhancements

1. **Scheduled Refreshes**
   - Auto-refresh URL datasets
   - Cron-like scheduling
   - Change detection

2. **Data Validation**
   - Schema validation
   - Data quality checks
   - Outlier detection

3. **Advanced Scraping**
   - JavaScript rendering (Playwright)
   - Pagination support
   - Login/authentication

4. **Data Transformation**
   - Pre-processing pipelines
   - Column mapping
   - Data cleaning

5. **Version Control**
   - Dataset versioning
   - Diff between versions
   - Rollback capability

---

## Dependencies

**Backend:**
- pandas >= 2.2.3
- openpyxl >= 3.1.5 (Excel)
- pyarrow >= 18.1.0 (Parquet)
- beautifulsoup4 >= 4.12.3 (Scraping)
- lxml >= 5.3.0 (HTML parsing)
- aiohttp >= 3.11.10 (Async HTTP)
- requests >= 2.32.3 (Sync HTTP)

**Frontend:**
- react >= 18.0.0
- axios >= 1.6.0
- react-router-dom >= 6.0.0

---

## Metrics & Monitoring

**Tracked Metrics:**
- Upload success rate
- Average upload time
- File size distribution
- Source type distribution
- Error rates by type

**Logs:**
- Upload attempts
- Processing errors
- File size violations
- Invalid file types

---

## Documentation

- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide (README)
- [ ] Architecture documentation
- [ ] This feature spec
