# Test Documentation

This directory contains comprehensive test documentation for the InsightForge Data Upload & Dataset Management feature.

## Test Report Files

### 1. data-upload-test.md
- **Format:** Markdown
- **Use:** Easy to read in any text editor or GitHub
- **Content:** Complete test report with all scenarios and results

### 2. data-upload-test.html
- **Format:** HTML with styling
- **Use:** Can be opened in Microsoft Word and saved as .docx
- **Content:** Same as markdown but formatted for Word

## How to Create .docx File

### Option 1: Using Microsoft Word
1. Open `data-upload-test.html` in Microsoft Word
2. Click File > Save As
3. Choose "Word Document (.docx)" as the format
4. Save as `data-upload-test.docx`

### Option 2: Using LibreOffice/OpenOffice
1. Open `data-upload-test.html` in LibreOffice Writer
2. Click File > Save As
3. Choose "Microsoft Word 2007-365 (.docx)" as the format
4. Save as `data-upload-test.docx`

### Option 3: Using Pandoc (Command Line)
```bash
pandoc data-upload-test.md -o data-upload-test.docx
```

## Test Summary

**Date:** January 26, 2026
**Status:** ✅ ALL TESTS PASSED
**Success Rate:** 100% (14/14 tests passed)

### Features Tested
- ✅ User Registration & Authentication
- ✅ CSV File Upload
- ✅ JSON File Upload
- ✅ Excel File Upload
- ✅ URL Data Import
- ✅ Web Scraping
- ✅ Dataset Listing
- ✅ Dataset Details
- ✅ Dataset Preview
- ✅ Dataset Deletion
- ✅ Schema Inference

## Test Data Files

Test files are located in the scratchpad directory:
- `test_sales_data.csv` - Sales data (10 rows, 6 columns)
- `test_employees.json` - Employee records (5 records)
- `test_products.xlsx` - Product catalog (5 rows, 5 columns)

## Accessing the Application

After starting with `docker-compose up`:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Test Credentials

- **Email:** test@example.com
- **Password:** password123

## Running Tests Again

To re-run the tests:

1. Start the services:
   ```bash
   docker-compose up -d
   ```

2. Register a new user or use existing credentials

3. Test file upload:
   ```bash
   TOKEN="your-access-token"
   curl -X POST http://localhost:8000/api/datasets/upload \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test_sales_data.csv" \
     -F "name=Sales Data" \
     -F "description=Test upload"
   ```

4. Test URL import:
   ```bash
   curl -X POST http://localhost:8000/api/datasets/from-url \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test Dataset","url":"https://example.com/data.csv"}'
   ```

5. Test web scraping:
   ```bash
   curl -X POST http://localhost:8000/api/datasets/scrape \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"Scraped Data","url":"https://www.w3schools.com/html/html_tables.asp"}'
   ```

## Next Steps

The feature is production-ready. Recommended enhancements:
1. Add monitoring for upload failures
2. Implement rate limiting for URL imports
3. Add file virus scanning
4. Implement detailed logging
5. Add UI for progress indicators and better error messages
