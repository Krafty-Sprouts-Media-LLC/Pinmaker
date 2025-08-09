#!/usr/bin/env python3
"""
Test image upload to identify the exact 500 error
"""

import requests
import json
from PIL import Image
import io

def test_image_upload():
    base_url = "https://api.pinmaker.kraftysprouts.com"
    
    print("🔍 Testing image upload to identify 500 error...")
    print("=" * 60)
    
    # Create a simple test image
    print("\n1. Creating test image...")
    test_image = Image.new('RGB', (200, 200), color='white')
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Test the actual analyze endpoint
    print("\n2. Testing /api/v1/analyze endpoint...")
    try:
        files = {'file': ('test.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        response = requests.post(f"{base_url}/api/v1/analyze", files=files, timeout=60)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Upload successful!")
            data = response.json()
            print(f"   Analysis ID: {data.get('analysis_id')}")
        else:
            print(f"   ❌ Upload failed with status {response.status_code}")
            print(f"   Response Text: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"   Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Error: {response.text}")
                
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (60 seconds)")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test complete!")

if __name__ == "__main__":
    test_image_upload()
