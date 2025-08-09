#!/usr/bin/env python3
import requests
from PIL import Image
import io
import time

print("🧪 Testing lightweight image analysis...")

# Create test image
test_image = Image.new('RGB', (100, 100), color='white')
img_byte_arr = io.BytesIO()
test_image.save(img_byte_arr, format='JPEG')
img_byte_arr.seek(0)

# Test the analyze endpoint
start_time = time.time()
try:
    files = {'file': ('test.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    response = requests.post("https://api.pinmaker.kraftysprouts.com/api/v1/analyze", files=files, timeout=35)
    
    elapsed_time = time.time() - start_time
    print(f"Status: {response.status_code}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Lightweight analysis working!")
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        print(f"Colors found: {len(data.get('colors', []))}")
        print(f"Fonts found: {len(data.get('fonts', []))}")
    else:
        print(f"❌ Still failing: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out (35 seconds)")
except Exception as e:
    print(f"❌ Error: {e}")

print("Test complete!")
