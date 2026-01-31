#!/usr/bin/env python3
"""Check backend settings"""
import sys
sys.path.insert(0, '/Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/backend')

from app.core.config import settings
import os

print("Backend Configuration Check")
print("=" * 60)
print(f"UPLOAD_DIR setting: {settings.UPLOAD_DIR}")
print(f"UPLOAD_DIR exists: {os.path.exists(settings.UPLOAD_DIR)}")
print(f"UPLOAD_DIR is writable: {os.access(settings.UPLOAD_DIR, os.W_OK) if os.path.exists(settings.UPLOAD_DIR) else 'N/A'}")
print(f"API_KEY (first 20 chars): {settings.API_KEY[:20] if settings.API_KEY else 'None'}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"DEBUG: {settings.DEBUG}")
print("=" * 60)

# Try to create a test file
test_file = os.path.join(settings.UPLOAD_DIR, "test.txt")
try:
    with open(test_file, "w") as f:
        f.write("test")
    print(f"✅ Successfully wrote test file to: {test_file}")
    os.remove(test_file)
    print(f"✅ Successfully deleted test file")
except Exception as e:
    print(f"❌ Error writing to upload directory: {e}")
