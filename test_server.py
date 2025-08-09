#!/usr/bin/env python3
"""
Test script to diagnose server issues
"""

import requests
import json
import sys

def test_server():
    base_url = "https://api.pinmaker.kraftysprouts.com"
    
    print("🔍 Testing Pinmaker API Server...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Diagnostics
    print("\n2. Testing diagnostics endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/diagnose", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Diagnostics available")
            data = response.json()
            print(f"   Services: {data.get('services', {})}")
            print(f"   Dependencies: {data.get('dependencies', {})}")
            if data.get('errors'):
                print(f"   ❌ Errors found: {data['errors']}")
        else:
            print("   ❌ Diagnostics failed")
    except Exception as e:
        print(f"   ❌ Diagnostics error: {e}")
    
    # Test 3: Test analyze with small image
    print("\n3. Testing basic image processing...")
    try:
        # Create a simple test image
        from PIL import Image
        import io
        
        # Create a 100x100 white image
        test_image = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        files = {'file': ('test.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        response = requests.post(f"{base_url}/api/v1/test-analyze", files=files, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Basic image processing works")
        else:
            print(f"   ❌ Basic image processing failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Test analyze error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

if __name__ == "__main__":
    test_server()
