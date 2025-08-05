# WhatsApp Image Generation API Agent

This API agent provides a RESTful interface to generate images using WhatsApp Web and ChatGPT, designed for integration with n8n workflows.

## 🚀 Features

- **RESTful API**: Simple HTTP endpoints for image generation
- **Persistent WhatsApp Session**: Maintains browser session across requests
- **Thread-Safe**: Handles concurrent requests safely
- **Error Handling**: Comprehensive error detection and reporting
- **Health Monitoring**: Health check endpoint for monitoring
- **Automatic Directory Creation**: Creates target directories automatically

## 📋 Prerequisites

1. **WhatsApp Web Setup**:
   - WhatsApp Web must be logged in
   - ChatGPT contact must be pinned in WhatsApp Web
   - Initial session setup required

2. **Python Dependencies**:
   ```bash
   pip install -r api_requirements.txt
   playwright install
   ```

3. **Directory Structure**:
   ```
   /Users/devanshc/Desktop/ProteinPapaPanda/
   ├── <reel_number>/
   │   └── images/
   │       └── <snippet_number>.png
   ```

## 🏃‍♂️ Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r api_requirements.txt
   playwright install
   ```

2. **Setup WhatsApp Session**:
   - Run the agent: `python3 whatsapp_image_api_agent.py`
   - The agent will open WhatsApp Web
   - Log in to WhatsApp Web manually (first time only)
   - Ensure ChatGPT contact is pinned

3. **Test the API**:
   ```bash
   curl -X POST http://localhost:5000/generate-image \
     -H "Content-Type: application/json" \
     -d '{
       "reel_number": "1",
       "snippet_number": "001",
       "image_prompt": "A beautiful sunset over mountains"
     }'
   ```

## 🔌 API Endpoints

### 1. Health Check
**GET** `/health`

Returns the health status of the API and WhatsApp session.

**Response**:
```json
{
  "status": "healthy",
  "whatsapp_session": true,
  "timestamp": "2025-01-27T10:30:00.000Z"
}
```

### 2. Generate Image
**POST** `/generate-image`

Generates an image using the provided prompt and saves it to the specified path.

**Request Body**:
```json
{
  "reel_number": "1",
  "snippet_number": "001", 
  "image_prompt": "A beautiful sunset over mountains"
}
```

**Success Response**:
```json
{
  "success": true,
  "message": "Image generated successfully",
  "file_path": "/Users/devanshc/Desktop/ProteinPapaPanda/1/images/001.png",
  "reel_number": "1",
  "snippet_number": "001"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Image generation failed or timed out"
}
```

### 3. Initialize Session
**POST** `/initialize-session`

Manually initialize the WhatsApp session (usually not needed as it's done automatically).

**Response**:
```json
{
  "success": true,
  "message": "WhatsApp session initialized successfully"
}
```

## 🔧 n8n Integration

### HTTP Request Node Configuration

#### 1. Generate Image Request

**Method**: `POST`
**URL**: `http://localhost:5000/generate-image`
**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "reel_number": "{{ $json.reel_number }}",
  "snippet_number": "{{ $json.snippet_number }}",
  "image_prompt": "{{ $json.image_prompt }}"
}
```

#### 2. Health Check Request

**Method**: `GET`
**URL**: `http://localhost:5000/health`

### n8n Workflow Example

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5000/generate-image",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "reel_number",
              "value": "{{ $json.reel_number }}"
            },
            {
              "name": "snippet_number", 
              "value": "{{ $json.snippet_number }}"
            },
            {
              "name": "image_prompt",
              "value": "{{ $json.image_prompt }}"
            }
          ]
        }
      },
      "name": "Generate Image",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1
    }
  ]
}
```

### Error Handling in n8n

Add an **IF** node after the HTTP request to handle errors:

**Condition**: `{{ $json.success === false }}`

**True Branch**: Error handling (e.g., send notification, retry logic)
**False Branch**: Success handling (e.g., continue workflow)

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# WhatsApp Configuration
WHATSAPP_CHAT_NAME=ChatGPT
WHATSAPP_TIMEOUT_MINUTES=10

# File Paths
BASE_SAVE_PATH=/Users/devanshc/Desktop/ProteinPapaPanda
```

### Customization

You can modify the following in `whatsapp_image_api_agent.py`:

1. **Timeout Duration**: Change `timeout_minutes=10` in `wait_for_image_generation()`
2. **Save Path**: Modify the path in `generate_single_image()`
3. **Retry Logic**: Adjust `max_retries=3` in `send_prompt_with_retry()`

## 🐛 Troubleshooting

### Common Issues

1. **WhatsApp Session Not Initialized**:
   - Ensure WhatsApp Web is logged in
   - Check if ChatGPT contact is pinned
   - Restart the API agent

2. **Image Generation Timeout**:
   - Increase timeout duration
   - Check internet connection
   - Verify ChatGPT is responding

3. **Download Failures**:
   - Check file permissions for save directory
   - Ensure sufficient disk space
   - Verify WhatsApp Web is not blocked

### Logs

The API provides detailed logging. Check the console output for:
- Session initialization status
- Prompt sending attempts
- Image generation progress
- Download status
- Error messages

## 🔒 Security Considerations

1. **Network Security**: The API runs on `0.0.0.0:5000` by default
2. **Authentication**: Consider adding API key authentication for production
3. **Rate Limiting**: Implement rate limiting for production use
4. **Input Validation**: All inputs are validated but consider additional sanitization

## 📊 Performance

- **Typical Response Time**: 2-10 minutes (depending on image generation time)
- **Concurrent Requests**: Supported with thread-safe implementation
- **Session Persistence**: WhatsApp session maintained across requests
- **Memory Usage**: ~200-500MB (depending on browser session)

## 🔄 Production Deployment

For production deployment, consider:

1. **Process Manager**: Use PM2 or systemd
2. **Reverse Proxy**: Nginx or Apache
3. **SSL/TLS**: HTTPS encryption
4. **Monitoring**: Health checks and logging
5. **Backup**: Regular session backups

## 📝 Example Usage

### cURL Example
```bash
curl -X POST http://localhost:5000/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "reel_number": "1",
    "snippet_number": "001",
    "image_prompt": "A professional headshot of a business person"
  }'
```

### Python Example
```python
import requests

response = requests.post('http://localhost:5000/generate-image', json={
    'reel_number': '1',
    'snippet_number': '001',
    'image_prompt': 'A professional headshot of a business person'
})

if response.json()['success']:
    print(f"Image saved to: {response.json()['file_path']}")
else:
    print(f"Error: {response.json()['error']}")
```

## 📞 Support

For issues or questions:
1. Check the logs for error messages
2. Verify WhatsApp Web setup
3. Test with the health check endpoint
4. Review the troubleshooting section above 