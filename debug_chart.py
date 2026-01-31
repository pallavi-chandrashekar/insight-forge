#!/usr/bin/env python3
"""Debug chart generation issue"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login
print("1. Logging in...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@insightforge.com",
    "password": "testpass123"
})
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Error: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   Token obtained: {token[:30]}...")

# Get datasets
print("\n2. Getting datasets...")
response = requests.get(f"{BASE_URL}/datasets/", headers=headers)
print(f"   Status: {response.status_code}")
datasets = response.json()
print(f"   Found {len(datasets)} dataset(s)")

if not datasets:
    print("   ERROR: No datasets found!")
    exit(1)

dataset_id = datasets[0]["id"]
print(f"   Using dataset: {dataset_id}")
print(f"   Dataset name: {datasets[0]['name']}")
print(f"   File path: {datasets[0].get('file_path', 'N/A')}")

# Try to generate chart
print("\n3. Attempting to generate bar chart...")
viz_request = {
    "dataset_id": dataset_id,
    "chart_type": "bar",
    "config": {
        "x_column": "category",
        "y_column": "sales",
        "aggregation": "sum",
        "title": "Test Bar Chart"
    },
    "name": "Debug Test Chart"
}

print(f"   Request: {json.dumps(viz_request, indent=2)}")

response = requests.post(
    f"{BASE_URL}/visualize/generate",
    headers=headers,
    json=viz_request
)

print(f"\n4. Response:")
print(f"   Status: {response.status_code}")
print(f"   Body: {response.text}")

if response.status_code == 201 or response.status_code == 200:
    print("\n✅ SUCCESS! Chart generated.")
    viz = response.json()
    print(f"   Visualization ID: {viz.get('id')}")
    print(f"   Chart type: {viz.get('chart_type')}")
    print(f"   Has chart_data: {viz.get('chart_data') is not None}")
else:
    print("\n❌ FAILED! Chart generation error.")
    try:
        error = response.json()
        print(f"   Error detail: {error.get('detail', 'Unknown error')}")
    except:
        print(f"   Raw error: {response.text}")
