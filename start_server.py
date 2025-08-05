#!/usr/bin/env python3
"""
Start the improved API server with queue system
"""

import subprocess
import sys
import os

def start_server():
    """Start the improved API server"""
    try:
        print("🚀 Starting improved WhatsApp Image Generation API Server...")
        print("📋 Features:")
        print("   ✅ Queue system for concurrent requests")
        print("   ✅ Google Sheets integration")
        print("   ✅ Batch image generation per reel")
        print("   ✅ Organized file structure")
        print("   ✅ No browser conflicts")
        print("   ✅ Better error handling")
        print("   ✅ Sequential processing")
        print("=" * 50)
        
        # Start the server
        result = subprocess.run([sys.executable, 'simple_http_server.py'], 
                              capture_output=False, text=True)
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Starting WhatsApp Image Generation API...")
    success = start_server()
    
    if not success:
        print("\n❌ Failed to start server!")
        print("💡 Make sure to run cleanup first:")
        print("   python3 run_cleanup.py") 