# InsightForge Visualization Testing

This directory contains comprehensive test documentation and test data for the InsightForge visualization feature.

## Files

### Test Documentation
- **visualization-test.md** - Markdown version of the test document
- **visualization-test.docx** - Word document format (primary test document)

### Test Data
Located in `test-data/` directory:
- **sales_sample.csv** - Sample product sales data (30 rows, 7 columns)
- **temperature_sample.csv** - Sample weather data (20 rows, 5 columns)

## Test Document Contents

The test document includes:
1. **35 comprehensive test scenarios** covering:
   - Dataset upload and management
   - AI-powered visualization suggestions (Claude AI)
   - All 9 chart types (bar, line, scatter, pie, histogram, heatmap, box, area, table)
   - Chart configuration and customization
   - Chart interactivity (zoom, pan, hover)
   - Chart export functionality
   - Saved visualizations management
   - Error handling and validation
   - API endpoint testing
   - Security testing
   - UI/UX testing

2. **Test setup instructions**
3. **Test data descriptions**
4. **Screenshot placeholders** for documenting results
5. **API request examples**
6. **Test results summary section**
7. **Issues tracking section**
8. **Recommendations section**

## How to Use This Test Document

### For Manual Testing

1. **Open the DOCX file** (`visualization-test.docx`) in Microsoft Word or compatible software
2. **Follow the test environment setup** instructions
3. **Execute each test scenario** in order
4. **Check the checkboxes** (Pass/Fail/Blocked) as you complete each test
5. **Take screenshots** at indicated points and paste them into the document
6. **Document any issues** found in the Issues section
7. **Fill in the Test Results Summary** when complete
8. **Save the completed document** with test execution date

### For Automated Testing

The test scenarios can be used as a basis for:
- Selenium/Playwright E2E tests
- API integration tests with pytest
- Performance tests with Locust
- Security tests with OWASP ZAP

## Running the Tests

### Prerequisites

Ensure the InsightForge application is running:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Database
docker-compose up -d db

# Terminal 3 - Frontend
cd frontend
npm run dev
```

### Test Execution Order

1. **Setup Tests (TS-01 to TS-02)** - Verify basic setup
2. **AI Suggestion Tests (TS-03 to TS-07)** - Test Claude AI suggestions
3. **Manual Chart Tests (TS-08 to TS-11)** - Test each chart type
4. **Configuration Tests (TS-12 to TS-14)** - Test chart customization
5. **Interactivity Tests (TS-15 to TS-17)** - Test user interactions
6. **Persistence Tests (TS-18 to TS-20)** - Test save/load/delete
7. **Error Handling Tests (TS-21 to TS-26)** - Test edge cases
8. **API Tests (TS-27 to TS-30)** - Test backend endpoints
9. **Security Tests (TS-31 to TS-32)** - Test authentication/authorization
10. **UX Tests (TS-33 to TS-35)** - Test user experience

### Expected Duration

- **Full test suite:** 4-6 hours (including documentation)
- **Smoke test (key scenarios):** 1-2 hours
- **API tests only:** 30 minutes
- **Chart type tests only:** 1-2 hours

## Test Data Details

### Sales Sample Data
- **Purpose:** Test categorical, numeric, and time-series visualizations
- **Columns:**
  - date: Transaction dates (Jan-Feb 2024)
  - product: 15 different products
  - category: Electronics or Furniture
  - region: North, South, East, West
  - sales: Dollar amounts
  - quantity: Item counts
  - price: Unit prices
- **Best for:** Bar, line, scatter, pie charts

### Temperature Sample Data
- **Purpose:** Test scientific/weather data visualizations
- **Columns:**
  - date: Observation dates
  - city: 4 different cities
  - temperature: Fahrenheit values
  - humidity: Percentage values
  - precipitation: Inches
- **Best for:** Line, area, box, heatmap charts

## Key Test Scenarios

### Critical Path
These scenarios must pass for release:
- TS-01: Dataset Upload
- TS-03: AI Visualization Suggestions
- TS-04: Generate Bar Chart
- TS-05: Generate Line Chart
- TS-16: Chart Interactivity - Hover
- TS-27: API Endpoint - Suggest
- TS-28: API Endpoint - Generate
- TS-31: Security - Authentication

### High Priority
Important but not blocking:
- All remaining chart types (TS-06 to TS-11)
- Configuration options (TS-12 to TS-14)
- Error handling (TS-21 to TS-25)
- Saved visualizations (TS-18 to TS-20)

### Nice to Have
Can be deferred:
- Performance testing (TS-26)
- Responsive design (TS-33)
- Empty states (TS-35)

## Reporting Issues

When you find an issue:

1. **Document in the Issues section** of the test document
2. **Include:**
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots
   - Environment details
   - Severity (Critical/High/Medium/Low)
3. **Create GitHub issue** (if using issue tracker)
4. **Notify the development team**

## Success Criteria

The visualization feature is ready for release when:
- ✅ All critical path scenarios pass
- ✅ At least 90% of all scenarios pass
- ✅ No critical or high-severity issues remain open
- ✅ All 9 chart types render correctly
- ✅ AI suggestions work reliably
- ✅ Security tests pass
- ✅ API endpoints return correct responses
- ✅ Error handling is graceful

## Tips for Testers

1. **Test with different data types** - Try with your own datasets
2. **Test edge cases** - Empty datasets, single row, very large values
3. **Test browser compatibility** - Chrome, Firefox, Safari, Edge
4. **Clear cache between tests** - Avoid false positives from caching
5. **Check console logs** - Look for JavaScript errors
6. **Use browser DevTools** - Network tab for API calls, Console for errors
7. **Test with slow network** - Use browser throttling
8. **Test error recovery** - Can users recover from errors?

## Converting to Other Formats

The markdown file can be converted to other formats:

```bash
# To PDF
pandoc visualization-test.md -o visualization-test.pdf

# To HTML
pandoc visualization-test.md -o visualization-test.html --standalone

# To DOCX (already done)
pandoc visualization-test.md -o visualization-test.docx --toc
```

## Questions or Issues?

- Check the main project README
- Review the feature documentation at `docs/features/phase1/03-visualization.md`
- Contact the development team

---

**Last Updated:** 2024-01-26
**Test Document Version:** 1.0
