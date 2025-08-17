# Dreamina Upload API - Quick Summary

## What's New

I've created a complete Dreamina Upload API that automates uploading image-audio pairs to Dreamina's AI Avatar feature. The API processes files sequentially by reel number, exactly as you requested.

## Key Features

✅ **Sequential Processing**: Uploads files 1, 2, 3, etc. in order  
✅ **Error Handling**: Continues with next pair if one fails  
✅ **Queue System**: Handles concurrent requests properly  
✅ **Browser Automation**: Fully automated Dreamina navigation  
✅ **File Pairing**: Automatically matches image and audio files  

## Files Created

1. **`dreamina_upload_api_server.py`** - Main API server
2. **`start_dreamina_server.py`** - Startup script
3. **`test_dreamina_api.py`** - Test script
4. **`DREAMINA_UPLOAD_API_GUIDE.md`** - Complete documentation
5. **`DREAMINA_API_SUMMARY.md`** - This summary

## API Endpoints

- `GET /health` - Health check
- `POST /upload-reel-to-dreamina` - Upload files for a reel
- `GET /upload-status` - Check processing status

## Usage

### Start the Server
```bash
python3 start_dreamina_server.py
```

### Test the API
```bash
python3 test_dreamina_api.py
```

### API Call Example
```bash
curl -X POST http://localhost:5003/upload-reel-to-dreamina \
  -H "Content-Type: application/json" \
  -d '{"reel_number": "123"}'
```

## File Structure Expected

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

## How It Works

1. **Receives reel number** via API call
2. **Navigates to folders** for that reel number
3. **Finds file pairs** (1.jpg + 1.mp3, 2.jpg + 2.mp3, etc.)
4. **Uploads sequentially** - starts with pair 1
5. **Waits for generation** to complete
6. **Continues to pair 2** if successful
7. **Stops on error** and reports results

## n8n Integration

Perfect for n8n workflows:
- HTTP Request node to call the API
- Pass reel number from Google Sheets
- Handle success/failure responses
- Log results to database

## Dependencies Added

- `flask` - Added to requirements.txt

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Install Playwright: `playwright install chromium`
3. Start server: `python3 start_dreamina_server.py`
4. Test with: `python3 test_dreamina_api.py`
5. Integrate with your n8n workflow

The API is ready to use and will handle the complete Dreamina upload process automatically! 