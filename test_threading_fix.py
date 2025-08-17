#!/usr/bin/env python3
"""
Test script to check if the threading issue in WhatsApp API is resolved
"""

import requests
import threading
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

def test_single_request():
    """Test a single request to see if it works"""
    print(f"🔍 Testing single request at {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # First initialize session
        response = requests.post(f"{BASE_URL}/initialize-session", timeout=30)
        print(f"   Session init: {response.status_code}")
        
        if response.status_code != 200:
            print("   ❌ Session initialization failed")
            return False
        
        # Wait a bit
        time.sleep(5)
        
        # Test single image generation
        test_data = {
            "reel_number": "threading_test",
            "snippet_number": "001",
            "image_prompt": "A simple test image for threading check"
        }
        
        response = requests.post(
            f"{BASE_URL}/generate-image",
            json=test_data,
            timeout=120
        )
        
        print(f"   Image generation: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Single request successful")
            return True
        else:
            print(f"   ❌ Image generation failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_concurrent_requests():
    """Test multiple concurrent requests"""
    print(f"\n⚡ Testing concurrent requests at {datetime.now().strftime('%H:%M:%S')}")
    
    results = []
    errors = []
    
    def send_request(request_id):
        try:
            print(f"   Thread {request_id}: Starting request...")
            
            test_data = {
                "reel_number": f"concurrent_{request_id}",
                "snippet_number": "001",
                "image_prompt": f"Test image {request_id} for concurrent testing"
            }
            
            response = requests.post(
                f"{BASE_URL}/generate-image",
                json=test_data,
                timeout=60
            )
            
            print(f"   Thread {request_id}: Status {response.status_code}")
            results.append(response.status_code)
            
        except Exception as e:
            error_msg = f"Thread {request_id}: {str(e)}"
            print(f"   ❌ {error_msg}")
            errors.append(error_msg)
    
    # Send 3 concurrent requests
    threads = []
    for i in range(3):
        thread = threading.Thread(target=send_request, args=(i+1,))
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Small delay between thread starts
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"\n   Concurrent test results:")
    print(f"   Successful responses: {len([r for r in results if r == 200])}")
    print(f"   Failed responses: {len([r for r in results if r != 200])}")
    print(f"   Errors: {len(errors)}")
    
    if len(errors) == 0:
        print("   ✅ Concurrent requests handled successfully")
        return True
    else:
        print("   ❌ Concurrent requests had issues")
        for error in errors:
            print(f"     {error}")
        return False

def main():
    """Run threading tests"""
    print("🧪 WhatsApp API Threading Test")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Single request
    single_success = test_single_request()
    
    if not single_success:
        print("\n❌ Single request failed. Cannot proceed with concurrent testing.")
        return False
    
    # Wait between tests
    print("\n⏳ Waiting 10 seconds before concurrent test...")
    time.sleep(10)
    
    # Test 2: Concurrent requests
    concurrent_success = test_concurrent_requests()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 THREADING TEST SUMMARY")
    print("=" * 50)
    
    if single_success and concurrent_success:
        print("🎉 All threading tests passed! The issue appears to be resolved.")
        return True
    elif single_success and not concurrent_success:
        print("⚠️  Single requests work, but concurrent requests still have issues.")
        return False
    else:
        print("❌ Basic functionality is broken. Check the API server.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        exit(1) 