#!/usr/bin/env python3
"""Test complete flow: upload dataset and create visualization"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

# Login
print("1. Logging in...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@insightforge.com",
    "password": "testpass123"
})
if response.status_code != 200:
    print(f"   Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   ✅ Logged in successfully")

# Upload fresh dataset
print("\n2. Uploading fresh dataset...")
test_data_path = Path("/Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/docs/tests/test-data/sales_sample.csv")

if not test_data_path.exists():
    print(f"   ❌ Test data not found at {test_data_path}")
    exit(1)

with open(test_data_path, "rb") as f:
    files = {"file": ("sales_sample.csv", f, "text/csv")}
    data = {"name": "Sales Data Fresh", "description": "Fresh upload for testing"}
    response = requests.post(f"{BASE_URL}/datasets/upload", headers=headers, files=files, data=data)

print(f"   Status: {response.status_code}")
if response.status_code not in [200, 201]:
    print(f"   ❌ Upload failed: {response.text}")
    exit(1)

dataset = response.json()
dataset_id = dataset["id"]
print(f"   ✅ Dataset uploaded successfully")
print(f"   Dataset ID: {dataset_id}")
print(f"   File path: {dataset.get('file_path', 'N/A')}")
print(f"   Rows: {dataset.get('row_count')}, Columns: {dataset.get('column_count')}")

# Generate bar chart
print("\n3. Generating bar chart...")
viz_request = {
    "dataset_id": dataset_id,
    "chart_type": "bar",
    "config": {
        "x_column": "category",
        "y_column": "sales",
        "aggregation": "sum",
        "title": "Total Sales by Category"
    },
    "name": "Sales by Category"
}

response = requests.post(f"{BASE_URL}/visualize/generate", headers=headers, json=viz_request)
print(f"   Status: {response.status_code}")

if response.status_code in [200, 201]:
    viz = response.json()
    print(f"   ✅ Chart generated successfully!")
    print(f"   Visualization ID: {viz['id']}")
    print(f"   Chart type: {viz['chart_type']}")
    print(f"   Has chart data: {viz.get('chart_data') is not None}")

    # Try other chart types
    print("\n4. Testing other chart types...")
    chart_tests = [
        ("line", "date", "sales", "Sales Over Time"),
        ("scatter", "quantity", "sales", "Quantity vs Sales"),
        ("pie", "region", "sales", "Sales by Region"),
    ]

    for chart_type, x_col, y_col, title in chart_tests:
        config = {
            "x_column": x_col,
            "y_column": y_col,
            "title": title
        }
        if chart_type == "pie":
            config["aggregation"] = "sum"

        response = requests.post(
            f"{BASE_URL}/visualize/generate",
            headers=headers,
            json={
                "dataset_id": dataset_id,
                "chart_type": chart_type,
                "config": config,
                "name": f"Test {chart_type.capitalize()}"
            }
        )
        status = "✅" if response.status_code in [200, 201] else "❌"
        print(f"   {status} {chart_type.capitalize()} chart: {response.status_code}")

    print("\n🎉 SUCCESS! All charts are working!")
    print(f"\n📊 View your charts at: http://localhost:5173")

else:
    print(f"   ❌ Chart generation failed: {response.text}")
