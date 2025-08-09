#!/usr/bin/env python3
import requests

print("🔍 Testing server status...")

try:
    # Test health endpoint
    response = requests.get("https://api.pinmaker.kraftysprouts.com/api/v1/health", timeout=10)
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Server is responding!")
    else:
        print(f"❌ Server returned {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection failed - server might be down")
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")

print("Test complete!")
