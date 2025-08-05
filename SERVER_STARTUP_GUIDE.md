# Server Startup Guide

## 🚀 Quick Start Commands

### **Step 1: Navigate to Project Directory**
```bash
cd "/Users/devanshc/Documents/cursor projects/n8n_faceless_agent"
```

### **Step 2: Start WhatsApp Image Generation API Server**
```bash
python3 start_server.py
```
- **Port**: 5001
- **Health Check**: `http://localhost:5001/health`
- **Endpoint**: `POST http://localhost:5001/generate-reel-images`

### **Step 3: Start Audio Download API Server (In New Terminal)**
```bash
python3 start_audio_server.py
```
- **Port**: 5002
- **Health Check**: `http://localhost:5002/health`
- **Endpoint**: `POST http://localhost:5002/download-reel-audio`

## 📋 Detailed Startup Instructions

### **Prerequisites**
Make sure you have all dependencies installed:
```bash
pip install playwright gspread oauth2client python-dotenv requests flask
playwright install
```

### **Starting Both Servers**

#### **Option 1: Separate Terminal Windows (Recommended)**

**Terminal 1 - Image Generation API:**
```bash
cd "/Users/devanshc/Documents/cursor projects/n8n_faceless_agent"
python3 start_server.py
```

**Terminal 2 - Audio Download API:**
```bash
cd "/Users/devanshc/Documents/cursor projects/n8n_faceless_agent"
python3 start_audio_server.py
```

#### **Option 2: Background Processes**
```bash
cd "/Users/devanshc/Documents/cursor projects/n8n_faceless_agent"

# Start Image Generation API in background
nohup python3 start_server.py > image_api.log 2>&1 &

# Start Audio Download API in background
nohup python3 start_audio_server.py > audio_api.log 2>&1 &
```

### **Verifying Servers Are Running**

#### **Check Image Generation API:**
```bash
curl -X GET http://localhost:5001/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "message": "WhatsApp Image Generation API is running",
  "queue_size": 0,
  "is_processing": false
}
```

#### **Check Audio Download API:**
```bash
curl -X GET http://localhost:5002/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Audio Download API is running",
  "queue_size": 0,
  "is_processing": false
}
```

## 🔧 N8N Configuration

### **Image Generation API**
- **URL**: `http://host.docker.internal:5001/generate-reel-images`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "reel_number": "{{ $json.reel_number }}"
}
```

### **Audio Download API**
- **URL**: `http://host.docker.internal:5002/download-reel-audio`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "reel_number": "{{ $json.reel_number }}"
}
```

## 🛠️ Troubleshooting

### **Port Already in Use**
If you get "Address already in use" error:

**For Port 5001 (Image Generation):**
```bash
# Find the process using port 5001
lsof -ti:5001

# Kill the process
kill -9 $(lsof -ti:5001)

# Restart the server
python3 start_server.py
```

**For Port 5002 (Audio Download):**
```bash
# Find the process using port 5002
lsof -ti:5002

# Kill the process
kill -9 $(lsof -ti:5002)

# Restart the server
python3 start_audio_server.py
```

### **Server Not Responding**
1. **Check if servers are running:**
   ```bash
   ps aux | grep python3
   ```

2. **Check logs:**
   ```bash
   # For background processes
   tail -f image_api.log
   tail -f audio_api.log
   ```

3. **Restart servers:**
   ```bash
   # Kill all Python processes
   pkill -f "python3.*server"
   
   # Restart servers
   python3 start_server.py &
   python3 start_audio_server.py &
   ```

### **Docker Connection Issues**
If n8n can't connect to the APIs:

1. **Check if servers are accessible from Docker:**
   ```bash
   # Test from within Docker container
   curl -X GET http://host.docker.internal:5001/health
   curl -X GET http://host.docker.internal:5002/health
   ```

2. **Alternative URLs to try:**
   - `http://host.docker.internal:5001`
   - `http://172.17.0.1:5001`
   - `http://localhost:5001` (if running n8n locally)

## 📊 Server Status Monitoring

### **Real-time Queue Monitoring**
Both APIs provide queue status in their health endpoints:
- `queue_size`: Number of requests waiting
- `is_processing`: Whether a request is currently being processed

### **Log Files**
- **Image Generation**: Check terminal output or `image_api.log`
- **Audio Download**: Check terminal output or `audio_api.log`

## 🔄 Stopping Servers

### **Graceful Shutdown**
Press `Ctrl+C` in each terminal window where servers are running.

### **Force Stop**
```bash
# Kill all server processes
pkill -f "python3.*server"

# Or kill by port
kill -9 $(lsof -ti:5001)
kill -9 $(lsof -ti:5002)
```

## 📁 File Organization

### **Image Generation Output**
```
/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/images/
├── 1.png
├── 2.png
├── 3.png
└── 4.png
```

### **Audio Download Output**
```
/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/Audio/
├── 1.mp3
├── 2.mp3
├── 3.mp3
└── 4.mp3
```

## ⚡ Quick Reference

### **Start Both Servers:**
```bash
cd "/Users/devanshc/Documents/cursor projects/n8n_faceless_agent"
python3 start_server.py &      # Image Generation API (Port 5001)
python3 start_audio_server.py & # Audio Download API (Port 5002)
```

### **Test Both APIs:**
```bash
# Test Image Generation API
curl -X POST http://localhost:5001/generate-reel-images \
  -H "Content-Type: application/json" \
  -d '{"reel_number": "1"}'

# Test Audio Download API
curl -X POST http://localhost:5002/download-reel-audio \
  -H "Content-Type: application/json" \
  -d '{"reel_number": "1"}'
```

### **Stop All Servers:**
```bash
pkill -f "python3.*server"
```

## 🎯 Success Indicators

### **Image Generation API**
- ✅ Server starts without errors
- ✅ Health check returns 200 OK
- ✅ Queue system initializes
- ✅ WhatsApp session loads successfully

### **Audio Download API**
- ✅ Server starts without errors
- ✅ Health check returns 200 OK
- ✅ Queue system initializes
- ✅ Google Sheets connection works

Both servers are now ready for n8n integration! 