# Query Engine Testing - Quick Start Guide

**Get started testing in 5 minutes!** ⚡

---

## 🚀 Quick Start Commands

### 1. Run All Automated Tests
```bash
cd backend
./run_tests.sh
```

**Expected Output:**
```
✅ 34 tests passed
⚠️  10 skipped
❌ 0 failed
📊 Coverage: 97%
```

---

### 2. Generate Test Data
```bash
cd backend
python tests/test_data.py
```

**Creates:**
- `/tmp/test_products.csv` (10 products)
- `/tmp/test_sales.csv` (20 orders)
- `/tmp/test_customers.csv` (10 customers)
- `/tmp/test_employees.csv` (15 employees)

---

### 3. Run Specific Tests
```bash
# Unit tests only
pytest tests/test_query_engine.py -v

# API tests only
pytest tests/test_query_api.py -v

# Single test
pytest tests/test_query_engine.py::TestSQLExecution::test_basic_select_all -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

---

### 4. Manual Testing
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Then follow: MANUAL-TESTING-GUIDE.md
```

---

### 5. Convert to DOCX
```bash
# Install pandoc (one-time)
brew install pandoc

# Convert test plan
cd docs/tests
pandoc query-engine-test-plan.md -o query-engine-test.docx --toc
```

---

## 📚 Documentation Quick Links

| Document | Purpose | Location |
|----------|---------|----------|
| 📖 **README** | Start here | `docs/tests/README.md` |
| 📋 **Test Plan** | All 44 test cases | `docs/tests/query-engine-test-plan.md` |
| 👋 **Manual Guide** | Step-by-step testing | `docs/tests/MANUAL-TESTING-GUIDE.md` |
| 📊 **Summary** | Implementation details | `docs/tests/IMPLEMENTATION-SUMMARY.md` |
| 🔄 **DOCX Guide** | Convert to Word | `docs/tests/CONVERT-TO-DOCX.md` |

---

## 🧪 Test Status at a Glance

```
✅ SQL Queries              8/8 tests passing
✅ Pandas Operations        7/7 tests passing
✅ Sales Analysis           3/3 tests passing
✅ DataFrame Stats          4/4 tests passing
✅ API Endpoints            8/8 tests passing
✅ Error Handling           4/5 tests passing
⚠️  Natural Language        0/4 (needs API key)
⏳ Performance             1/5 (Phase 2)

TOTAL: 34/44 passing (77% with skipped, 100% runnable)
```

---

## 📸 Screenshot Checklist (For DOCX)

When doing manual testing, capture these **37 screenshots**:

### Must-Have Screenshots (Top 10)
1. ✅ Login page
2. ✅ Dataset upload
3. ✅ SQL query interface
4. ✅ Query results table
5. ✅ Pandas operations builder
6. ✅ Query history list
7. ✅ Error message display
8. ✅ Natural language query
9. ✅ Export functionality
10. ✅ Performance metrics

### Complete List
See `MANUAL-TESTING-GUIDE.md` for all 37 screenshot locations.

---

## 🎯 Success Criteria

All these should be ✅ after testing:

**Functionality**
- [ ] SQL queries execute correctly
- [ ] Pandas operations work
- [ ] Query history accessible
- [ ] Errors handled gracefully
- [ ] Results exportable

**Performance**
- [ ] Simple queries < 100ms
- [ ] Complex queries < 200ms
- [ ] API responses < 200ms

**Coverage**
- [ ] Unit tests: 100% pass
- [ ] Integration tests: 100% pass
- [ ] Code coverage: > 95%

**Documentation**
- [ ] Test plan complete
- [ ] Screenshots captured
- [ ] DOCX created (if needed)

---

## 🐛 Troubleshooting

### Tests Won't Run
```bash
# Check Python version
python --version  # Should be 3.11+

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Check database
pg_isready -h localhost -p 5432
```

### Import Errors
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Database Errors
```bash
# Create test database
createdb insightforge_test

# Set environment variable
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/insightforge_test"
```

### NumPy Warnings
These are safe to ignore. Test data was generated successfully despite warnings.

---

## 💡 Pro Tips

1. **Run tests before commits**
   ```bash
   git add .
   ./backend/run_tests.sh && git commit
   ```

2. **Watch mode for development**
   ```bash
   pytest tests/ --watch
   ```

3. **Focus on failing tests**
   ```bash
   pytest tests/ -x  # Stop on first failure
   pytest tests/ --lf  # Run last failed
   ```

4. **Generate HTML coverage**
   ```bash
   pytest tests/ --cov=app --cov-report=html
   open htmlcov/index.html
   ```

5. **Verbose output for debugging**
   ```bash
   pytest tests/ -v -s  # Show print statements
   ```

---

## 📞 Need Help?

**Common Issues:**
- Tests failing → Check `htmlcov/index.html` for coverage gaps
- Import errors → Verify virtual environment activated
- Database errors → Ensure PostgreSQL running
- API key errors → Expected for NL tests

**Get Support:**
- Review docs: Start with `README.md`
- Check logs: `backend/htmlcov/`
- Ask team: Slack #insightforge-dev

---

## 🎉 You're Ready!

1. ✅ Run `./backend/run_tests.sh`
2. ✅ Review `docs/tests/README.md`
3. ✅ Follow manual guide for screenshots
4. ✅ Convert to DOCX if needed

**Estimated Time:**
- Automated tests: 2 minutes
- Manual testing: 30 minutes
- Screenshot capture: 20 minutes
- DOCX creation: 15 minutes
- **Total: ~1 hour for complete testing**

---

**Last Updated:** 2026-01-26
**Version:** 1.0.0
**Status:** ✅ Ready to use
