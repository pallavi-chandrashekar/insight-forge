# 🚀 InsightForge Visualization Testing - Quick Start

## ✅ Current Status: READY TO TEST

Both servers are running and ready:
- **Backend:** http://localhost:8000 ✅
- **Frontend:** http://localhost:5173 ✅
- **API Docs:** http://localhost:8000/docs ✅

---

## 🎯 Start Testing NOW

### 1. Open Your Browser
```
http://localhost:5173
```

### 2. Create Test Account
- Click "Register" or "Sign Up"
- Email: `tester@insightforge.com`
- Password: `testpass123`
- Name: `Test User`

### 3. Upload Test Data
Navigate to Upload page and upload:
- `docs/tests/test-data/sales_sample.csv`
- `docs/tests/test-data/temperature_sample.csv`

### 4. Try Visualization
- Go to "Visualize" page
- Select a dataset
- Click "Get AI Suggestions" (will show error - needs API key)
- Try manual chart creation

---

## 📋 Test Scenarios

Follow these test scenarios from the test document:
- **TS-01:** Dataset Upload ✅ (working)
- **TS-02:** Navigate to Visualization Page ✅ (working)
- **TS-03:** AI Suggestions ⚠️ (needs API key)
- **TS-04-11:** Chart Types ❌ (backend bug)

Full test document: `docs/tests/visualization-test.docx`

---

## 🔍 Known Issues

### Issue #1: Chart Generation Fails
- **What:** All chart types return HTTP 500 error
- **Why:** Backend file path handling bug
- **Impact:** Cannot create visualizations yet
- **Status:** Under investigation

### Issue #2: AI Suggestions Disabled
- **What:** "Get AI Suggestions" button won't work
- **Why:** Placeholder API key in use
- **Fix:** Add real Anthropic API key to backend/.env
- **Current Key:** `sk-ant-test-key-placeholder`

---

## 🛠️ Quick Fixes

### If Backend Not Responding
```bash
cd /Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### If Frontend Not Responding
```bash
cd /Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/frontend
npm run dev
```

### To Add Real API Key
```bash
cd backend
# Edit .env file
nano .env
# Change: API_KEY=sk-ant-test-key-placeholder
# To:     API_KEY=sk-ant-your-real-key-here
# Save and restart backend
```

---

## 📊 What You CAN Test Right Now

Even with the issues, you can test:
1. ✅ User registration and login
2. ✅ Dataset upload (CSV, JSON, Excel)
3. ✅ Dataset preview and schema
4. ✅ Dataset listing
5. ✅ Navigation between pages
6. ✅ UI responsiveness
7. ✅ Error messages for invalid inputs

## 📊 What's BLOCKED

These require fixing the chart generation bug:
- ❌ Creating any visualizations
- ❌ Chart interactivity testing
- ❌ Chart configuration testing
- ❌ Save/load visualizations

---

## 🧪 API Testing

Run the automated API test suite:
```bash
cd /Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/backend
source venv/bin/activate
python3 ../test_api.py
```

**Current Results:** 7 passed, 5 failed

---

## 📚 Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Feature Docs | `docs/features/phase1/03-visualization.md` | Complete feature specification |
| Test Plan | `docs/tests/visualization-test.docx` | 35 detailed test scenarios |
| Test Data | `docs/tests/test-data/*.csv` | Sample datasets for testing |
| Status Report | `TESTING_STATUS.md` | Current testing status |
| This Guide | `QUICK_START.md` | Quick start guide |

---

## 🎯 Next Steps Priority

1. **High Priority:** Fix chart generation bug
   - Debug file path issue in backend
   - Check uploads directory permissions
   - Test with simple bar chart

2. **Medium Priority:** Add real API key
   - Get Anthropic API key
   - Update .env file
   - Test AI suggestions

3. **Low Priority:** Manual UI testing
   - Test what works (upload, preview)
   - Document UI issues
   - Take screenshots

---

## 💡 Tips

- Keep browser console open (F12) to see any errors
- Check Network tab to see API calls
- Backend logs at `/tmp/backend.log`
- All test data in `docs/tests/test-data/`

---

## ❓ Need Help?

- Review `TESTING_STATUS.md` for detailed status
- Check `docs/tests/visualization-test.docx` for test procedures
- API documentation at http://localhost:8000/docs
- Backend logs: `tail -f /tmp/backend.log`

---

**Last Updated:** 2026-01-26 17:40
**Status:** 🟢 Servers Running | 🟡 Partial Functionality | 🔴 Chart Generation Broken
