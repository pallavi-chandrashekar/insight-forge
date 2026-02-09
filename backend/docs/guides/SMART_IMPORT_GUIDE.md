# Smart Import System - Documentation

## Overview

The Smart Import system intelligently detects what type of URL a user provides and guides them to the appropriate feature.

**Problem Solved:**
- Users previously could only import direct data file URLs (CSV, JSON, etc.)
- Providing documentation links (Medium articles, GitHub READMEs, etc.) would cause errors
- No guidance on what to do with dataset pages (Kaggle, etc.)

**Solution:**
- Automatically detect URL type (data, documentation, or dataset page)
- Extract documentation content and create context files
- Provide clear guidance for each URL type

---

## Supported URL Types

### 1. Data Files (Direct Import)

**Can be imported directly as datasets**

Examples:
- `https://example.com/data.csv`
- `https://api.example.com/export.json`
- `https://storage.example.com/report.xlsx`
- `https://data.example.com/dataset.parquet`

Supported formats: `.csv`, `.json`, `.xlsx`, `.xls`, `.parquet`, `.tsv`

**What happens:**
- System detects it's a data file
- Shows "✅ Data File Detected"
- Allows direct import as dataset

---

### 2. Documentation (Context Creation)

**Automatically creates context files from documentation**

Examples:
- `https://medium.com/@user/article` - Medium articles
- `https://github.com/user/repo/README.md` - GitHub READMEs
- `https://docs.google.com/document/d/...` - Google Docs
- `https://notion.so/Dataset-Guide` - Notion pages
- `https://substack.com/p/article` - Substack posts
- `https://docs.example.com/guide` - Documentation sites

**What happens:**
1. System detects it's documentation
2. Shows "📚 Documentation Detected"
3. Extracts content from the page
4. Converts to markdown format
5. Creates a context file automatically
6. User can use this context for enhanced analysis

**User Benefits:**
- Paste any guide/article URL
- System automatically creates context
- No manual copy-paste needed
- Context enhances AI understanding of dataset

---

### 3. Dataset Pages (Guidance)

**Provides guidance to find download links**

Examples:
- `https://kaggle.com/datasets/user/dataset` - Kaggle
- `https://data.world/user/dataset` - Data.world
- `https://github.com/user/repo` - GitHub repositories
- `https://huggingface.co/datasets/...` - Hugging Face
- `https://zenodo.org/record/...` - Zenodo
- `https://figshare.com/articles/...` - Figshare

**What happens:**
- System detects it's a dataset page (not direct data)
- Shows "📊 Dataset Page Detected"
- Provides guidance: "Look for 'Download' button"
- Explains this page describes a dataset
- Suggests using page as context documentation
- Guides user to find actual data download link

---

## API Endpoints

### POST `/api/smart-import/analyze-url`

Analyze any URL and determine what to do with it.

**Request:**
```json
{
  "url": "https://medium.com/@user/article",
  "dataset_name": "Optional Dataset Name"
}
```

**Response:**
```json
{
  "url_type": "documentation",
  "platform": "Medium",
  "message": {
    "type": "info",
    "title": "📚 Documentation Detected",
    "message": "This is a Medium documentation page. Would you like to use this as context documentation for your dataset?",
    "action": "create_context",
    "action_label": "Create Context from Documentation",
    "details": "Context files help the AI understand your dataset better..."
  },
  "can_import_data": false,
  "can_create_context": true,
  "documentation_content": "# Article Title\n\n**Source:** https://...\n\n..."
}
```

### POST `/api/smart-import/create-context-from-url`

Create a context file from a documentation URL.

**Request:**
```json
{
  "url": "https://medium.com/@user/article",
  "dataset_name": "Enterprise RAG Guide"
}
```

**Response:**
```json
{
  "success": true,
  "context_id": "uuid-here",
  "context_name": "Enterprise RAG Guide",
  "message": "Context created successfully from documentation URL"
}
```

### GET `/api/smart-import/supported-platforms`

Get list of all supported platforms.

**Response:**
```json
{
  "data_platforms": {
    "supported_formats": [".csv", ".json", ".xlsx", ...],
    "examples": ["https://example.com/data.csv", ...]
  },
  "documentation_platforms": {
    "supported": ["Medium", "GitHub", "Google Docs", ...],
    "examples": ["https://github.com/user/repo/README.md", ...]
  },
  "dataset_platforms": {
    "supported": ["Kaggle", "Data.world", ...],
    "guidance": "These platforms require you to find the 'Download' button...",
    "examples": ["https://kaggle.com/datasets/...", ...]
  }
}
```

---

## Use Cases

### Use Case 1: Medium Article as Context

**Scenario:**
User wants to analyze a dataset but first wants to understand concepts from a Medium article.

**Example:**
```
Article: "Enterprise RAG: A Production Guide"
URL: https://medium.com/@pallavi9964/enterprise-rag-a-production-guide...
```

**Steps:**
1. User pastes Medium article URL
2. System detects: "📚 Documentation - Medium"
3. System extracts article content
4. System creates context file with article content
5. User can now ask questions that reference concepts from the article
6. AI uses article context to provide better answers

**Result:**
- ✅ System doesn't break
- ✅ Article becomes searchable context
- ✅ Enhanced analysis with domain knowledge

---

### Use Case 2: GitHub README as Context

**Scenario:**
User imports a dataset from GitHub and wants to use the README as context.

**Steps:**
1. User provides GitHub README URL
2. System detects: "📚 Documentation - GitHub"
3. System extracts README content
4. Creates context with dataset description
5. AI understands dataset structure from README

---

### Use Case 3: Kaggle Dataset Page

**Scenario:**
User pastes a Kaggle dataset page URL (not the download link).

**Steps:**
1. User provides: `https://kaggle.com/datasets/user/dataset`
2. System detects: "📊 Dataset Page - Kaggle"
3. System shows guidance:
   - "This is a Kaggle dataset page"
   - "Look for 'Download' button to get actual data file"
   - "You can also use this page as context documentation"
4. User has two options:
   - Find download link for data import
   - Use page description as context

**Result:**
- ✅ Clear guidance
- ✅ No confusion
- ✅ User knows what to do

---

## Content Extraction

### How It Works

The system uses these techniques to extract documentation content:

1. **Fetch URL**: HTTP GET request with timeout (30s max)
2. **Parse HTML**: BeautifulSoup extracts main content
3. **Clean Content**: Removes scripts, styles, navigation
4. **Convert to Markdown**: Preserves structure (headers, lists, paragraphs)
5. **Add Metadata**: Adds source URL and import timestamp

### Limitations

**Authentication Required:**
- Some platforms require login (e.g., Medium paywall articles)
- Google Docs may require authentication
- Private GitHub repos need tokens

**Rate Limiting:**
- Platforms may rate limit requests
- System has 30s timeout per URL

**Content Quality:**
- Depends on HTML structure
- Some sites may have poor extraction
- JavaScript-heavy sites may not work

**Workaround:**
If automatic extraction fails, users can:
- Copy content manually
- Create context file directly
- Use public/non-paywalled versions

---

## Architecture

### Components

**1. SmartURLDetector Service**
- `detect_url_type()`: Pattern matching for quick detection
- `inspect_url_content()`: HTTP fetch for unknown URLs
- `extract_documentation_from_url()`: HTML → Markdown conversion
- `generate_user_message()`: User-friendly guidance

**2. Smart Import Routes**
- `/analyze-url`: Determine URL type
- `/create-context-from-url`: Auto-create context
- `/supported-platforms`: List capabilities

**3. Context Service Integration**
- Auto-creates context from documentation
- Links to datasets via FK (Phase 2)
- Validates and stores context

### Detection Strategy

```
Step 1: Quick Pattern Match
├─ Check file extension (.csv, .json, etc.) → DATA_FILE
├─ Check domain (medium.com, github.com, etc.) → DOCUMENTATION
└─ Check dataset platform (kaggle.com, etc.) → DATASET_PAGE

Step 2: Content Inspection (if unknown)
├─ Fetch HTTP headers (Content-Type)
├─ Download first 5KB
├─ Analyze structure (CSV pattern? JSON? HTML?)
└─ Determine type

Step 3: Generate Guidance
├─ User-friendly message
├─ Suggested action
└─ Platform-specific instructions
```

---

## Security Considerations

### SSRF Protection

**Blocked Domains:**
- `localhost`
- `127.0.0.1`
- `0.0.0.0`
- `::1`
- Internal IP ranges

**Rationale:** Prevent Server-Side Request Forgery attacks

### Size Limits

- **Inspection:** 5KB max for content detection
- **Extraction:** 10MB max for documentation
- **Timeout:** 30 seconds per request

### User Isolation

- Only authenticated users can use smart import
- Contexts are user-scoped
- Cannot access other users' data

---

## Testing

See `test_smart_import_medium.py` for comprehensive tests:

**Test Coverage:**
- ✅ URL type detection (data, docs, dataset pages)
- ✅ Platform recognition (Medium, GitHub, etc.)
- ✅ Message generation
- ✅ Content extraction
- ✅ Complete flow simulation

**Run Tests:**
```bash
cd backend
python test_smart_import_medium.py
```

---

## Future Enhancements

### Phase 1 (Current)
- ✅ URL type detection
- ✅ Documentation extraction
- ✅ Context creation from URLs
- ✅ Support for major platforms

### Phase 2 (Planned)
- [ ] Frontend UI for smart import
- [ ] Preview before creating context
- [ ] Batch URL import
- [ ] OAuth for authenticated content

### Phase 3 (Future)
- [ ] PDF document extraction
- [ ] Video transcript extraction (YouTube, etc.)
- [ ] Slack/Discord message history
- [ ] Email thread extraction

---

## FAQ

**Q: What happens if I paste a Medium article URL?**
A: The system detects it's documentation, extracts the article content, and creates a context file. You can then use this context to enhance AI analysis.

**Q: Can I import data from Kaggle directly?**
A: Kaggle URLs are dataset pages, not direct data links. The system will guide you to find the "Download" button to get the actual data file URL.

**Q: What if the URL requires authentication?**
A: Content extraction may fail for authenticated content. You can manually copy the content and create a context file directly.

**Q: How is this different from the old system?**
A: Previously, non-data URLs would cause errors. Now, the system intelligently detects the URL type and guides you to the appropriate action.

**Q: Can I use GitHub private repositories?**
A: Not yet. Future versions may support OAuth tokens for authenticated content.

---

## Summary

**Before Smart Import:**
- ❌ Only data file URLs worked
- ❌ Documentation links caused errors
- ❌ No guidance for users
- ❌ Confusing error messages

**After Smart Import:**
- ✅ Data files → Import directly
- ✅ Documentation → Create context
- ✅ Dataset pages → Clear guidance
- ✅ User-friendly messages
- ✅ Supports 10+ platforms

**Result:**
The app is now **robust and intelligent** - it handles any URL users provide and guides them to the right action!
