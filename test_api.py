#!/usr/bin/env python3
"""
API Testing Script for InsightForge Visualization Feature
"""
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test data
TEST_USER = {
    "email": "test@insightforge.com",
    "password": "testpass123",
    "full_name": "Test User"
}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def add_result(self, test_name, passed, details=""):
        self.results.append({
            "test": test_name,
            "status": "PASS" if passed else "FAIL",
            "details": details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{'✅ PASS' if passed else '❌ FAIL'}: {test_name}")
        if details:
            print(f"  {details}")

    def print_summary(self):
        print("\n" + "="*60)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("="*60)

results = TestResults()

print("=" * 60)
print("InsightForge API Testing - Visualization Feature")
print("=" * 60)

# Test 1: Health Check
print("\n[Test 1] Health Check")
try:
    response = requests.get(f"{BASE_URL}/health")
    results.add_result(
        "Health endpoint",
        response.status_code == 200 and response.json().get("status") == "healthy",
        f"Status code: {response.status_code}"
    )
except Exception as e:
    results.add_result("Health endpoint", False, str(e))

# Test 2: Register User
print("\n[Test 2] User Registration")
try:
    response = requests.post(f"{API_URL}/auth/register", json=TEST_USER)
    if response.status_code in [200, 201]:
        results.add_result("Register new user", True, "User created successfully")
    elif response.status_code == 400 and "already registered" in response.text:
        results.add_result("Register user (already exists)", True, "User already exists")
    else:
        results.add_result("Register user", False, f"Status: {response.status_code}, {response.text}")
except Exception as e:
    results.add_result("Register user", False, str(e))

# Test 3: Login
print("\n[Test 3] User Login")
try:
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get("access_token")
        if TOKEN:
            results.add_result("User login", True, f"Token received (length: {len(TOKEN)})")
            # Save token for subsequent tests
            with open("/tmp/test_token.txt", "w") as f:
                f.write(TOKEN)
        else:
            results.add_result("User login", False, "No access token in response")
    else:
        results.add_result("User login", False, f"Status: {response.status_code}")
except Exception as e:
    results.add_result("User login", False, str(e))
    sys.exit(1)

# Get token for authenticated requests
try:
    with open("/tmp/test_token.txt", "r") as f:
        TOKEN = f.read().strip()
    HEADERS = {"Authorization": f"Bearer {TOKEN}"}
except:
    print("❌ Cannot continue without token")
    sys.exit(1)

# Test 4: Upload Dataset
print("\n[Test 4] Dataset Upload")
test_data_path = Path("/Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/docs/tests/test-data/sales_sample.csv")
if test_data_path.exists():
    try:
        with open(test_data_path, "rb") as f:
            files = {"file": ("sales_sample.csv", f, "text/csv")}
            data = {"name": "Product Sales Data", "description": "Test sales data"}
            response = requests.post(f"{API_URL}/datasets/upload", headers=HEADERS, files=files, data=data)

        if response.status_code in [200, 201]:
            dataset = response.json()
            DATASET_ID = dataset.get("id")
            with open("/tmp/test_dataset_id.txt", "w") as f:
                f.write(DATASET_ID)
            results.add_result("Upload CSV dataset", True, f"Dataset ID: {DATASET_ID}")
        else:
            results.add_result("Upload CSV dataset", False, f"Status: {response.status_code}, {response.text[:200]}")
    except Exception as e:
        results.add_result("Upload CSV dataset", False, str(e))
else:
    results.add_result("Upload CSV dataset", False, "Test data file not found")

# Get dataset ID
try:
    with open("/tmp/test_dataset_id.txt", "r") as f:
        DATASET_ID = f.read().strip()
except:
    print("❌ Cannot continue without dataset ID")
    results.print_summary()
    sys.exit(1)

# Test 5: List Datasets
print("\n[Test 5] List Datasets")
try:
    response = requests.get(f"{API_URL}/datasets/", headers=HEADERS)
    if response.status_code == 200:
        datasets = response.json()
        results.add_result("List datasets", True, f"Found {len(datasets)} dataset(s)")
    else:
        results.add_result("List datasets", False, f"Status: {response.status_code}")
except Exception as e:
    results.add_result("List datasets", False, str(e))

# Test 6: Get Dataset Preview
print("\n[Test 6] Dataset Preview")
try:
    response = requests.get(f"{API_URL}/datasets/{DATASET_ID}/preview", headers=HEADERS)
    if response.status_code == 200:
        preview = response.json()
        results.add_result("Dataset preview", True, f"Rows: {len(preview.get('data', []))}, Columns: {len(preview.get('columns', []))}")
    else:
        results.add_result("Dataset preview", False, f"Status: {response.status_code}")
except Exception as e:
    results.add_result("Dataset preview", False, str(e))

# Test 7: Get Visualization Suggestions (Note: Requires valid API key)
print("\n[Test 7] AI Visualization Suggestions")
try:
    response = requests.post(
        f"{API_URL}/visualize/suggest",
        headers=HEADERS,
        params={"dataset_id": DATASET_ID}
    )
    if response.status_code == 200:
        suggestions = response.json()
        results.add_result("AI suggestions", True, f"Received {len(suggestions)} suggestion(s)")
        # Save first suggestion for testing
        if suggestions:
            print(f"\n  First suggestion:")
            print(f"    Chart type: {suggestions[0].get('chart_type')}")
            print(f"    Title: {suggestions[0].get('title')}")
            print(f"    Confidence: {suggestions[0].get('confidence')}")
            with open("/tmp/test_suggestion.json", "w") as f:
                json.dump(suggestions[0], f)
    else:
        error_detail = response.json().get("detail", response.text)
        if "API" in error_detail or "api" in error_detail.lower():
            results.add_result("AI suggestions", False, f"LLM API key issue (expected with placeholder key)")
        else:
            results.add_result("AI suggestions", False, f"Status: {response.status_code}, {error_detail}")
except Exception as e:
    results.add_result("AI suggestions", False, str(e))

# Test 8: Generate Visualization (Manual)
print("\n[Test 8] Generate Visualization (Manual Config)")
viz_config = {
    "dataset_id": DATASET_ID,
    "chart_type": "bar",
    "config": {
        "x_column": "category",
        "y_column": "sales",
        "aggregation": "sum",
        "title": "Total Sales by Category"
    },
    "name": "Test Bar Chart"
}
try:
    response = requests.post(f"{API_URL}/visualize/generate", headers=HEADERS, json=viz_config)
    if response.status_code in [200, 201]:
        viz = response.json()
        VIZ_ID = viz.get("id")
        with open("/tmp/test_viz_id.txt", "w") as f:
            f.write(VIZ_ID)
        has_chart_data = viz.get("chart_data") is not None
        results.add_result("Generate bar chart", True, f"Viz ID: {VIZ_ID}, Has chart data: {has_chart_data}")
    else:
        results.add_result("Generate bar chart", False, f"Status: {response.status_code}, {response.text[:200]}")
except Exception as e:
    results.add_result("Generate bar chart", False, str(e))

# Test 9: List Visualizations
print("\n[Test 9] List Visualizations")
try:
    response = requests.get(f"{API_URL}/visualize/", headers=HEADERS)
    if response.status_code == 200:
        visualizations = response.json()
        results.add_result("List visualizations", True, f"Found {len(visualizations)} visualization(s)")
    else:
        results.add_result("List visualizations", False, f"Status: {response.status_code}")
except Exception as e:
    results.add_result("List visualizations", False, str(e))

# Test 10: Get Specific Visualization
print("\n[Test 10] Get Visualization by ID")
try:
    with open("/tmp/test_viz_id.txt", "r") as f:
        VIZ_ID = f.read().strip()
    response = requests.get(f"{API_URL}/visualize/{VIZ_ID}", headers=HEADERS)
    if response.status_code == 200:
        viz = response.json()
        results.add_result("Get visualization", True, f"Chart type: {viz.get('chart_type')}")
    else:
        results.add_result("Get visualization", False, f"Status: {response.status_code}")
except Exception as e:
    results.add_result("Get visualization", False, str(e))

# Test 11: Test Different Chart Types
print("\n[Test 11] Generate Different Chart Types")
chart_types = [
    ("line", "date", "sales", "Sales Over Time"),
    ("scatter", "price", "quantity", "Price vs Quantity"),
    ("pie", "region", "sales", "Sales by Region"),
]

for chart_type, x_col, y_col, title in chart_types:
    try:
        config = {
            "dataset_id": DATASET_ID,
            "chart_type": chart_type,
            "config": {
                "x_column": x_col,
                "y_column": y_col,
                "title": title
            },
            "name": f"Test {chart_type.capitalize()} Chart"
        }
        if chart_type == "pie":
            config["config"]["aggregation"] = "sum"

        response = requests.post(f"{API_URL}/visualize/generate", headers=HEADERS, json=config)
        if response.status_code in [200, 201]:
            results.add_result(f"Generate {chart_type} chart", True, f"Created: {title}")
        else:
            results.add_result(f"Generate {chart_type} chart", False, f"Status: {response.status_code}")
    except Exception as e:
        results.add_result(f"Generate {chart_type} chart", False, str(e))

# Test 12: Authentication Test (No Token)
print("\n[Test 12] Security - Unauthenticated Request")
try:
    response = requests.get(f"{API_URL}/datasets/")
    if response.status_code == 401:
        results.add_result("Reject unauthenticated request", True, "Correctly returned 401")
    else:
        results.add_result("Reject unauthenticated request", False, f"Status: {response.status_code} (expected 401)")
except Exception as e:
    results.add_result("Reject unauthenticated request", False, str(e))

# Print summary
results.print_summary()

print("\n✨ API testing complete!")
print(f"📊 Check http://localhost:5173 for frontend testing")
print(f"📚 API docs: http://localhost:8000/docs")
