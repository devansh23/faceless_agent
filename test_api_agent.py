#!/usr/bin/env python3
"""
Test script for WhatsApp Image API Agent
"""

import requests
import json
import time

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_generate_image():
    """Test the image generation endpoint"""
    print("\n🎨 Testing image generation...")
    
    test_data = {
        "reel_number": "test",
        "snippet_number": "001",
        "image_prompt": "A simple red circle on white background"
    }
    
    try:
        print(f"📤 Sending request: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            'http://localhost:5000/generate-image',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Image generated successfully!")
                print(f"📁 File saved to: {data.get('file_path')}")
                return True
            else:
                print(f"❌ Image generation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting WhatsApp Image API Agent Tests")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Make sure the API agent is running.")
        print("Run: python3 whatsapp_image_api_agent.py")
        return
    
    # Test image generation
    print("\n⏳ Starting image generation test...")
    print("This may take 2-10 minutes depending on image generation time.")
    
    if test_generate_image():
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Image generation test failed.")
        print("Check the API logs for more details.")

if __name__ == "__main__":
    main() 