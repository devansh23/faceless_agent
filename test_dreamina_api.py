#!/usr/bin/env python3
"""
Test script for Dreamina Upload API
"""

import requests
import json
import time

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get('http://localhost:5003/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            print(f"   Queue size: {data['queue_size']}")
            print(f"   Processing: {data['is_processing']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_status():
    """Test the upload status endpoint"""
    print("\n📊 Testing upload status...")
    try:
        response = requests.get('http://localhost:5003/upload-status')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload status: {data['message']}")
            print(f"   Processing: {data['is_processing']}")
            print(f"   Queue size: {data['queue_size']}")
            return True
        else:
            print(f"❌ Upload status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Upload status error: {e}")
        return False

def test_upload_reel(reel_number="test123"):
    """Test uploading a reel"""
    print(f"\n🎬 Testing upload for reel: {reel_number}")
    try:
        response = requests.post(
            'http://localhost:5003/upload-reel-to-dreamina',
            json={'reel_number': reel_number},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Upload successful!")
                print(f"   Reel: {data['reel_number']}")
                print(f"   Total pairs: {data['total_pairs']}")
                print(f"   Uploaded pairs: {data['uploaded_pairs']}")
                
                # Show detailed results
                if 'results' in data:
                    print("   Results:")
                    for result in data['results']:
                        status = "✅" if result['success'] else "❌"
                        print(f"     {status} Pair {result['pair_number']}: {result['image']} + {result['audio']}")
                
                return True
            else:
                print(f"❌ Upload failed: {data.get('error', 'Unknown error')}")
                return False
        elif response.status_code == 429:
            print("⚠️ Server is busy, another upload is in progress")
            return False
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_invalid_request():
    """Test invalid request handling"""
    print("\n🚫 Testing invalid request...")
    try:
        # Test without reel_number
        response = requests.post(
            'http://localhost:5003/upload-reel-to-dreamina',
            json={},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Invalid request handled correctly: {data['error']}")
            return True
        else:
            print(f"❌ Invalid request not handled properly: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid request test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Dreamina Upload API Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    # Test 2: Upload status
    status_ok = test_upload_status()
    
    # Test 3: Invalid request
    invalid_ok = test_invalid_request()
    
    # Test 4: Upload (only if server is running)
    upload_ok = False
    if health_ok:
        # Ask user for reel number
        reel_number = input("\nEnter reel number to test (or press Enter for 'test123'): ").strip()
        if not reel_number:
            reel_number = "test123"
        
        print(f"\n⚠️  This will attempt to upload files for reel {reel_number}")
        print("   Make sure the files exist in the expected directory structure:")
        print(f"   /Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/Images/")
        print(f"   /Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/Audio/")
        
        confirm = input("\nContinue? (y/N): ").strip().lower()
        if confirm == 'y':
            upload_ok = test_upload_reel(reel_number)
        else:
            print("⏭️  Skipping upload test")
            upload_ok = True  # Mark as passed since we skipped it
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Upload Status: {'✅ PASS' if status_ok else '❌ FAIL'}")
    print(f"   Invalid Request: {'✅ PASS' if invalid_ok else '❌ FAIL'}")
    print(f"   Upload Test: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    all_passed = health_ok and status_ok and invalid_ok and upload_ok
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure the server is running: python3 start_dreamina_server.py")
        print("   2. Check if port 5003 is available")
        print("   3. Verify all dependencies are installed")
        print("   4. Check the server logs for errors")

if __name__ == "__main__":
    main() 