#!/usr/bin/env python3
"""
Direct API Connection Test Script

This script tests the direct API connection between Netlify frontend and VPS backend.
Run this after deploying the direct API configuration changes.
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "https://pinmaker.kraftysprouts.com:8000"
API_PREFIX = "/api/v1"
NETLIFY_DOMAINS = [
    "https://pinmaker-frontend.netlify.app",
    "https://pinmaker.netlify.app",
    "https://krafty-sprouts-media-llc.netlify.app"
]

def test_health_endpoint():
    """Test the health endpoint directly."""
    print("\n=== Testing Health Endpoint ===")
    try:
        url = f"{API_BASE_URL}{API_PREFIX}/health"
        response = requests.get(url, timeout=10)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cors_headers(netlify_domain):
    """Test CORS configuration for a specific Netlify domain."""
    print(f"\n=== Testing CORS for {netlify_domain} ===")
    try:
        url = f"{API_BASE_URL}{API_PREFIX}/health"
        headers = {
            'Origin': netlify_domain,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        return 'access-control-allow-origin' in response.headers
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_api_endpoints():
    """Test various API endpoints."""
    print("\n=== Testing API Endpoints ===")
    endpoints = [
        f"{API_BASE_URL}{API_PREFIX}/health",
        f"{API_BASE_URL}{API_PREFIX}/fonts",
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {endpoint} - Status: {response.status_code}")
            results.append(response.status_code == 200)
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_gunicorn_binding():
    """Test if gunicorn is properly binding to all interfaces."""
    print("\n=== Testing Gunicorn Binding ===")
    try:
        # Test both with and without port in URL
        urls = [
            f"{API_BASE_URL}{API_PREFIX}/health",
            f"https://pinmaker.kraftysprouts.com{API_PREFIX}/health"  # Without port
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                print(f"✓ {url} - Status: {response.status_code}")
            except Exception as e:
                print(f"✗ {url} - Error: {e}")
                
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests."""
    print(f"Direct API Connection Test - {datetime.now()}")
    print(f"Testing API at: {API_BASE_URL}")
    
    # Test basic connectivity
    health_ok = test_health_endpoint()
    
    # Test CORS for each Netlify domain
    cors_results = []
    for domain in NETLIFY_DOMAINS:
        cors_ok = test_cors_headers(domain)
        cors_results.append(cors_ok)
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    # Test gunicorn binding
    test_gunicorn_binding()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Health Endpoint: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"CORS Configuration: {'✓ PASS' if any(cors_results) else '✗ FAIL'}")
    print(f"API Endpoints: {'✓ PASS' if api_ok else '✗ FAIL'}")
    
    if health_ok and any(cors_results) and api_ok:
        print("\n🎉 Direct API connection is working correctly!")
        print("Your Netlify frontend should now be able to connect directly to the VPS API.")
    else:
        print("\n⚠️  Some tests failed. Check the deployment and configuration.")
        print("Refer to DIRECT_API_SETUP.md for troubleshooting steps.")

if __name__ == "__main__":
    main()