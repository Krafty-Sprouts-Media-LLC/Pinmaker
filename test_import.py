#!/usr/bin/env python3
"""
Test script to check if main.py can be imported successfully
This will help identify import errors that prevent gunicorn from loading the app
"""

import sys
import traceback

print("Testing import of main module...")
print(f"Python path: {sys.path}")
print(f"Current working directory: {sys.path[0]}")

try:
    print("\nAttempting to import main module...")
    import main
    print("✅ Successfully imported main module")
    
    if hasattr(main, 'app'):
        print("✅ Found 'app' attribute in main module")
        print(f"App type: {type(main.app)}")
    else:
        print("❌ 'app' attribute not found in main module")
        print(f"Available attributes: {[attr for attr in dir(main) if not attr.startswith('_')]}")
        
except ImportError as e:
    print(f"❌ ImportError: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\nTest completed.")
