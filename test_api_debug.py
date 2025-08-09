#!/usr/bin/env python3
import requests
import json
import sys
from pathlib import Path

def test_api_endpoints():
    """Test the backend API endpoints to identify the 500 error cause"""
    base_url = "https://api.pinmaker.kraftysprouts.com"
    
    print("🔍 Testing Backend API Endpoints...\n")
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Analyze endpoint with invalid data
    print("\n3. Testing analyze endpoint (no file)...")
    try:
        response = requests.post(f"{base_url}/api/v1/analyze", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Analyze endpoint with empty form data
    print("\n4. Testing analyze endpoint (empty form)...")
    try:
        response = requests.post(f"{base_url}/api/v1/analyze", files={}, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Analyze endpoint with dummy file
    print("\n5. Testing analyze endpoint (dummy text file)...")
    try:
        files = {'file': ('test.txt', 'dummy content', 'text/plain')}
        response = requests.post(f"{base_url}/api/v1/analyze", files=files, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}..." if len(response.text) > 500 else f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Check if favicon.ico exists for testing
    favicon_path = Path("frontend/public/favicon.ico")
    if favicon_path.exists():
        print("\n6. Testing analyze endpoint (favicon.ico)...")
        try:
            with open(favicon_path, 'rb') as f:
                files = {'file': ('favicon.ico', f, 'image/x-icon')}
                response = requests.post(f"{base_url}/api/v1/analyze", files=files, timeout=60)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:500]}..." if len(response.text) > 500 else f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("\n6. Skipping favicon test (file not found)")

if __name__ == "__main__":
    test_api_endpoints()