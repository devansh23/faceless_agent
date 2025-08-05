#!/usr/bin/env python3
"""
Start the Audio Download API server with queue system
"""

import subprocess
import sys
import os

def start_audio_server():
    """Start the Audio Download API server"""
    try:
        print("🎵 Starting Audio Download API Server...")
        print("📋 Features:")
        print("   ✅ Queue system for concurrent requests")
        print("   ✅ Google Sheets integration")
        print("   ✅ Batch audio download per reel")
        print("   ✅ Organized file structure")
        print("   ✅ Google Drive URL handling")
        print("   ✅ Better error handling")
        print("   ✅ Sequential processing")
        print("=" * 50)
        
        # Start the server
        result = subprocess.run([sys.executable, 'audio_download_api_server.py'], 
                              capture_output=False, text=True)
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Audio server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting audio server: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Starting Audio Download API...")
    success = start_audio_server()
    
    if not success:
        print("\n❌ Failed to start audio server!")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install flask requests gspread oauth2client python-dotenv") 