# 🧪 WhatsApp Image API Testing Guide

This guide will help you test all endpoints of the WhatsApp Image Generation API to ensure it's working correctly for n8n integration.

## 📋 Prerequisites

1. **WhatsApp API Server Running**: Make sure `start_image_server.py` is running on port 5001
2. **Python Dependencies**: Install required packages: `pip install requests`
3. **WhatsApp Web Ready**: Ensure you have a ChatGPT contact pinned in WhatsApp Web

## 🚀 Quick Start Testing

### Option 1: Python Test Script (Recommended)
```bash
# Run comprehensive test suite
python3 test_whatsapp_api.py
```

### Option 2: Manual Testing with curl
```bash
# Make script executable and run
chmod +x test_whatsapp_api_curl.sh
./test_whatsapp_api_curl.sh
```

### Option 3: Individual curl Commands
```bash
# Test each endpoint manually
curl -X GET http://127.0.0.1:5001/health
curl -X POST http://127.0.0.1:5001/initialize-session
```

## 🔍 Testing Each Endpoint

### 1. Health Check Endpoint
**URL**: `GET /health`
**Purpose**: Verify API is running and accessible

```bash
curl -X GET http://127.0.0.1:5001/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "whatsapp_session": false,
  "timestamp": "2025-08-15T15:49:23"
}
```

### 2. Session Initialization
**URL**: `POST /initialize-session`
**Purpose**: Initialize WhatsApp Web session

```bash
curl -X POST http://127.0.0.1:5001/initialize-session
```

**Expected Response**:
```json
{
  "success": true,
  "message": "WhatsApp session initialized successfully"
}
```

**Note**: This will open a browser window. You may need to scan QR code or confirm login.

### 3. Single Image Generation
**URL**: `POST /generate-image`
**Purpose**: Generate a single image from a prompt

```bash
curl -X POST http://127.0.0.1:5001/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "reel_number": "test",
    "snippet_number": "001",
    "image_prompt": "A simple red circle on white background"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Image generated successfully",
  "file_path": "images/test/001.png",
  "reel_number": "test",
  "snippet_number": "001"
}
```

### 4. Batch Image Generation
**URL**: `POST /generate-reel-images`
**Purpose**: Generate multiple images for a reel

```bash
curl -X POST http://127.0.0.1:5001/generate-reel-images \
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
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Batch processing completed. 2 successful, 0 failed",
  "reel_number": "test_batch",
  "total_snippets": 2,
  "successful_count": 2,
  "failed_count": 0,
  "results": [...]
}
```

## ⚠️ Testing Error Handling

### Missing Required Fields
```bash
curl -X POST http://127.0.0.1:5001/generate-image \
  -H "Content-Type: application/json" \
  -d '{"reel_number": "test"}'
```

**Expected Response**: `400 Bad Request` with error message

### Invalid Data Types
```bash
curl -X POST http://127.0.0.1:5001/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "reel_number": "test",
    "snippet_number": "001",
    "image_prompt": ""
  }'
```

**Expected Response**: `400 Bad Request` with validation error

## 🔧 Troubleshooting Common Issues

### 1. "WhatsApp session not initialized"
**Solution**: Call `/initialize-session` endpoint first

### 2. "cannot switch to a different thread"
**Solution**: This is the threading issue we're testing. The API should handle this gracefully.

### 3. Browser not opening
**Solution**: Check if Playwright is properly installed and the session directory exists

### 4. Image generation timeout
**Solution**: Increase timeout values in your n8n workflow

## 📊 Testing Checklist

- [ ] Health endpoint responds with 200
- [ ] Session initialization succeeds
- [ ] Single image generation works
- [ ] Batch image generation works
- [ ] Error handling works correctly
- [ ] Concurrent requests don't cause threading issues
- [ ] Images are downloaded to correct locations
- [ ] API responses include proper status codes

## 🎯 n8n Integration Testing

Once basic API testing passes, test with n8n:

1. **Create HTTP Request nodes** for each endpoint
2. **Set proper timeouts** (120s for image generation)
3. **Handle response status codes** in your workflow
4. **Test error scenarios** to ensure robust integration

## 🚨 Important Notes

1. **Session Persistence**: WhatsApp sessions are maintained between requests
2. **Image Generation Time**: Allow 2-5 minutes for image generation
3. **Browser Control**: Don't close the browser manually during testing
4. **File Locations**: Images are saved to `images/{reel_number}/{snippet_number}.png`

## 📝 Test Results Logging

Keep track of your test results:

```bash
# Run tests and save output
python3 test_whatsapp_api.py > test_results.log 2>&1

# Check for specific errors
grep "ERROR\|FAIL" test_results.log
```

## 🔄 Continuous Testing

For ongoing development, consider:

1. **Automated testing** in CI/CD pipeline
2. **Health monitoring** with regular health checks
3. **Performance testing** with load testing tools
4. **Integration testing** with actual n8n workflows

---

**Need Help?** Check the logs in your terminal where the API server is running for detailed error information. 