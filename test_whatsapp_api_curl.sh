#!/bin/bash

# WhatsApp Image API Testing Script (curl-based)
# Make sure the API server is running on port 5001

BASE_URL="http://127.0.0.1:5001"
echo "🧪 Testing WhatsApp Image API at $BASE_URL"
echo "=================================================="

# Test 1: Health Check
echo -e "\n🔍 Testing Health Endpoint..."
curl -s -X GET "$BASE_URL/health" | jq '.'

# Test 2: Initialize Session
echo -e "\n🚀 Testing Session Initialization..."
curl -s -X POST "$BASE_URL/initialize-session" | jq '.'

# Wait for session to stabilize
echo -e "\n⏳ Waiting 5 seconds for session to stabilize..."
sleep 5

# Test 3: Single Image Generation
echo -e "\n🎨 Testing Single Image Generation..."
curl -s -X POST "$BASE_URL/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "reel_number": "test",
    "snippet_number": "001",
    "image_prompt": "A simple red circle on white background"
  }' | jq '.'

# Wait between tests
echo -e "\n⏳ Waiting 10 seconds before batch test..."
sleep 10

# Test 4: Batch Image Generation
echo -e "\n🔄 Testing Batch Image Generation..."
curl -s -X POST "$BASE_URL/generate-reel-images" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | jq '.'

# Test 5: Error Handling - Missing Fields
echo -e "\n⚠️  Testing Error Handling - Missing Fields..."
curl -s -X POST "$BASE_URL/generate-image" \
  -H "Content-Type: application/json" \
  -d '{"reel_number": "test"}' | jq '.'

# Test 6: Error Handling - Invalid Data
echo -e "\n⚠️  Testing Error Handling - Invalid Data..."
curl -s -X POST "$BASE_URL/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "reel_number": "test",
    "snippet_number": "001",
    "image_prompt": ""
  }' | jq '.'

echo -e "\n✅ Testing completed!"
echo "Check the responses above for any errors." 