# Dreamina Upload API Guide

## Overview

The Dreamina Upload API provides automated upload functionality for image-audio pairs to Dreamina's AI Avatar feature. It processes files sequentially by reel number, handling browser automation and error recovery.

## Features

- ✅ **Queue System**: Handles concurrent requests sequentially
- ✅ **Sequential Upload**: Processes file pairs one by one (1, 2, 3, etc.)
- ✅ **Error Handling**: Continues with next pair if one fails
- ✅ **Progress Tracking**: Detailed logging and status updates
- ✅ **Browser Automation**: Automated navigation and file upload
- ✅ **File Pairing**: Automatically matches image and audio files by number

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns server status and queue information.

**Response:**
```json
{
  "status": "healthy",
  "message": "Dreamina Upload API is running",
  "timestamp": "2025-08-05T17:50:00.000000",
  "queue_size": 0,
  "is_processing": false
}
```

### 2. Upload Reel to Dreamina
```
POST /upload-reel-to-dreamina
```

**Request Body:**
```json
{
  "reel_number": "123"
}
```

**Response:**
```json
{
  "success": true,
  "reel_number": "123",
  "total_pairs": 5,
  "uploaded_pairs": 3,
  "results": [
    {
      "pair_number": 1,
      "image": "1.jpg",
      "audio": "1.mp3",
      "success": true
    },
    {
      "pair_number": 2,
      "image": "2.jpg",
      "audio": "2.mp3",
      "success": true
    },
    {
      "pair_number": 3,
      "image": "3.jpg",
      "audio": "3.mp3",
      "success": false
    }
  ]
}
```

### 3. Upload Status
```
GET /upload-status
```
Returns current processing status.

**Response:**
```json
{
  "is_processing": false,
  "queue_size": 0,
  "message": "Dreamina Upload API Status"
}
```

## File Structure Requirements

The API expects files to be organized in the following structure:

```
/Users/devanshc/Desktop/ProteinPapaPanda/
├── {reel_number}/
│   ├── Images/
│   │   ├── 1.jpg
│   │   ├── 2.jpg
│   │   └── 3.jpg
│   └── Audio/
│       ├── 1.mp3
│       ├── 2.mp3
│       └── 3.mp3
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install flask requests playwright python-dotenv
```

### 2. Install Playwright Browsers
```bash
playwright install chromium
```

### 3. Start the Server
```bash
python3 start_dreamina_server.py
```

The server will start on `http://localhost:5003`

## Usage Examples

### Using curl
```bash
# Health check
curl http://localhost:5003/health

# Upload reel 123
curl -X POST http://localhost:5003/upload-reel-to-dreamina \
  -H "Content-Type: application/json" \
  -d '{"reel_number": "123"}'

# Check status
curl http://localhost:5003/upload-status
```

### Using Python
```python
import requests

# Upload a reel
response = requests.post(
    'http://localhost:5003/upload-reel-to-dreamina',
    json={'reel_number': '123'}
)

if response.status_code == 200:
    result = response.json()
    print(f"Uploaded {result['uploaded_pairs']}/{result['total_pairs']} pairs")
else:
    print(f"Error: {response.json()['error']}")
```

## n8n Integration

### 1. HTTP Request Node Configuration

**Method:** POST  
**URL:** `http://localhost:5003/upload-reel-to-dreamina`  
**Headers:** `Content-Type: application/json`  
**Body:** 
```json
{
  "reel_number": "{{ $json.reel_number }}"
}
```

### 2. Response Handling

The API returns detailed information about the upload process:

- `success`: Overall success status
- `reel_number`: The processed reel number
- `total_pairs`: Total number of file pairs found
- `uploaded_pairs`: Number of successfully uploaded pairs
- `results`: Detailed results for each pair

### 3. Error Handling

The API handles various error scenarios:

- **Missing files**: Continues with available pairs
- **Upload failures**: Stops at first failure and reports
- **Browser errors**: Automatic retry and recovery
- **Network issues**: Timeout handling and error reporting

## Workflow Integration

### Typical n8n Workflow

1. **Trigger**: New reel data from Google Sheets
2. **HTTP Request**: Call Dreamina Upload API
3. **Condition**: Check upload success
4. **Notification**: Send status update
5. **Database**: Log results

### Example Workflow JSON
```json
{
  "nodes": [
    {
      "name": "Google Sheets Trigger",
      "type": "n8n-nodes-base.googleSheetsTrigger"
    },
    {
      "name": "Dreamina Upload",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5003/upload-reel-to-dreamina",
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
              "value": "={{ $json.reel_number }}"
            }
          ]
        }
      }
    },
    {
      "name": "Check Success",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true
          },
          "conditions": [
            {
              "leftValue": "={{ $json.success }}",
              "rightValue": true
            }
          ]
        }
      }
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Address already in use
   Port 5003 is in use by another program
   ```
   **Solution:** Stop the existing process or change the port

2. **Browser Launch Failed**
   ```
   ❌ Failed to launch browser
   ```
   **Solution:** Ensure Playwright is installed: `playwright install chromium`

3. **File Not Found**
   ```
   ❌ Images directory not found
   ```
   **Solution:** Verify the file structure matches the expected format

4. **Upload Elements Not Found**
   ```
   ❌ Image upload input not found
   ```
   **Solution:** The website structure may have changed; check selectors

### Debug Mode

Enable debug logging by modifying the server:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

### Manual Testing

Test the file structure manually:
```python
import os
reel_number = "123"
base_path = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}"
print(f"Images exist: {os.path.exists(f'{base_path}/Images')}")
print(f"Audio exists: {os.path.exists(f'{base_path}/Audio')}")
```

## Configuration

### Environment Variables

Create a `.env` file for configuration:
```env
DREAMINA_USER_DATA_DIR=vpn_browser_session
DREAMINA_HEADLESS=false
DREAMINA_TIMEOUT=300
```

### Custom File Paths

Modify the `get_file_pairs` method to use different paths:
```python
def get_file_pairs(self, reel_number):
    base_path = f"/your/custom/path/{reel_number}"
    # ... rest of the method
```

## Security Considerations

- The API runs on localhost by default
- No authentication is implemented (add if needed)
- Browser session data is stored locally
- File paths are validated before processing

## Performance Notes

- Each upload takes 2-5 minutes depending on file size
- Browser automation adds overhead
- Queue system prevents concurrent uploads
- Timeout is set to 5 minutes per generation

## Support

For issues or questions:
1. Check the logs in the terminal
2. Verify file structure and permissions
3. Test with a simple reel first
4. Check browser compatibility

## Changelog

### v1.0.0 (2025-08-05)
- Initial release
- Basic upload functionality
- Queue system
- Error handling
- n8n integration support 