#!/usr/bin/env python3
import requests
import sys
from pathlib import Path

def test_image_upload():
    """Test image upload to reproduce the 500 error"""
    base_url = "https://api.pinmaker.kraftysprouts.com"
    
    print("🔍 Testing Image Upload to Reproduce 500 Error...\n")
    
    # Test with the created PNG image
    image_path = Path("test_image.png")
    if not image_path.exists():
        print("❌ test_image.png not found!")
        return
    
    print(f"📁 Testing with: {image_path} ({image_path.stat().st_size} bytes)")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            print("🚀 Sending POST request to /api/v1/analyze...")
            
            response = requests.post(
                f"{base_url}/api/v1/analyze", 
                files=files, 
                timeout=60
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            if response.status_code == 500:
                print("🔥 500 ERROR REPRODUCED!")
                print(f"💥 Response Text: {response.text}")
                
                # Try to get more details
                try:
                    error_data = response.json()
                    print(f"📄 Error JSON: {error_data}")
                except:
                    print("❌ Could not parse error as JSON")
            else:
                print(f"✅ Success! Response: {response.text[:200]}...")
                
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 60 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Connection error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_upload()