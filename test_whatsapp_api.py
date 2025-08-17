#!/usr/bin/env python3
"""
WhatsApp Image API Testing Script
Tests all endpoints of the WhatsApp Image Generation API
"""

import requests
import json
import time
import os
from datetime import datetime

# API Configuration
BASE_URL = "http://127.0.0.1:5001"
API_ENDPOINTS = {
    "health": f"{BASE_URL}/health",
    "initialize": f"{BASE_URL}/initialize-session",
    "single_image": f"{BASE_URL}/generate-image",
    "batch_images": f"{BASE_URL}/generate-reel-images"
}

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(API_ENDPOINTS["health"], timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ Health check passed")
            return True
        else:
            print("   ❌ Health check failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_session_initialization():
    """Test WhatsApp session initialization"""
    print("\n🚀 Testing Session Initialization...")
    try:
        response = requests.post(API_ENDPOINTS["initialize"], timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ Session initialization passed")
            return True
        else:
            print("   ❌ Session initialization failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Session initialization error: {e}")
        return False

def test_single_image_generation():
    """Test single image generation"""
    print("\n🎨 Testing Single Image Generation...")
    
    test_data = {
        "reel_number": "test",
        "snippet_number": "001",
        "image_prompt": "A simple red circle on white background"
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["single_image"],
            json=test_data,
            timeout=300  # 5 minutes timeout for image generation
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ Single image generation passed")
            return True
        else:
            print("   ❌ Single image generation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Single image generation error: {e}")
        return False

def test_batch_image_generation():
	"""Test parallel batch image generation"""
	print("\n🔄 Testing Parallel Batch Image Generation...")
	
	test_data = {
		"reel_number": "test_batch",
		"snippets": [
			{
				"snippet_number": "001",
				"image_prompt": "A blue square on white background"
			},
			{
				"snippet_number": "002", 
				"image_prompt": "A green triangle on white background"
			}
		]
	}
	
	try:
		response = requests.post(
			API_ENDPOINTS["batch_images"],
			json=test_data,
			timeout=300  # 5 minutes timeout for parallel batch generation
		)
		print(f"   Status Code: {response.status_code}")
		print(f"   Response: {response.json()}")
		
		if response.status_code == 200:
			print("   ✅ Parallel batch image generation passed")
			return True
		else:
			print("   ❌ Parallel batch image generation failed")
			return False
			
	except Exception as e:
		print(f"   ❌ Parallel batch image generation error: {e}")
		return False

def test_error_handling():
    """Test API error handling with invalid data"""
    print("\n⚠️  Testing Error Handling...")
    
    # Test missing fields
    print("   Testing missing fields...")
    invalid_data = {"reel_number": "test"}
    
    try:
        response = requests.post(
            API_ENDPOINTS["single_image"],
            json=invalid_data,
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400:
            print("   ✅ Missing fields validation passed")
        else:
            print("   ❌ Missing fields validation failed")
            
    except Exception as e:
        print(f"   ❌ Missing fields test error: {e}")
    
    # Test invalid data types
    print("   Testing invalid data types...")
    invalid_data = {
        "reel_number": "test",
        "snippet_number": "001",
        "image_prompt": ""  # Empty prompt
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["single_image"],
            json=invalid_data,
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400:
            print("   ✅ Invalid data validation passed")
        else:
            print("   ❌ Invalid data validation failed")
            
    except Exception as e:
        print(f"   ❌ Invalid data test error: {e}")

def test_concurrent_requests():
    """Test handling of concurrent requests"""
    print("\n⚡ Testing Concurrent Request Handling...")
    
    test_data = {
        "reel_number": "concurrent_test",
        "snippet_number": "001",
        "image_prompt": "A yellow star on white background"
    }
    
    # Send multiple requests simultaneously
    import threading
    
    results = []
    errors = []
    
    def send_request():
        try:
            response = requests.post(
                API_ENDPOINTS["single_image"],
                json=test_data,
                timeout=60
            )
            results.append(response.status_code)
        except Exception as e:
            errors.append(str(e))
    
    # Send 3 concurrent requests
    threads = []
    for i in range(3):
        thread = threading.Thread(target=send_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"   Concurrent requests completed:")
    print(f"   Successful responses: {len([r for r in results if r == 200])}")
    print(f"   Failed responses: {len([r for r in results if r != 200])}")
    print(f"   Errors: {len(errors)}")
    
    if len(errors) == 0:
        print("   ✅ Concurrent request handling passed")
    else:
        print("   ⚠️  Concurrent request handling had issues")
        for error in errors:
            print(f"     Error: {error}")

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🧪 WhatsApp Image API - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Health Check
    test_results.append(("Health Check", test_health_endpoint()))
    
    # Test 2: Session Initialization
    test_results.append(("Session Initialization", test_session_initialization()))
    
    # Wait a bit for session to stabilize
    if test_results[-1][1]:
        print("\n⏳ Waiting 5 seconds for session to stabilize...")
        time.sleep(5)
    
    # Test 3: Single Image Generation
    test_results.append(("Single Image Generation", test_single_image_generation()))
    
    # Wait between tests
    print("\n⏳ Waiting 10 seconds before batch test...")
    time.sleep(10)
    
    # Test 4: Batch Image Generation
    test_results.append(("Batch Image Generation", test_batch_image_generation()))
    
    # Test 5: Error Handling
    test_error_handling()
    
    # Test 6: Concurrent Requests
    test_concurrent_requests()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        exit(1) 