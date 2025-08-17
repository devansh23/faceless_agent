#!/usr/bin/env python3
"""
Startup script for Dreamina Upload API Server
"""

import subprocess
import sys
import os

def main():
    print("🎬 Starting Dreamina Upload API...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(script_dir, 'dreamina_upload_api_server.py')
    
    try:
        print("🎵 Starting Dreamina Upload API Server...")
        print("📋 Features:")
        print("   ✅ Queue system for concurrent requests")
        print("   ✅ Sequential file pair upload")
        print("   ✅ Error handling and recovery")
        print("   ✅ Progress tracking")
        print("   ✅ Browser automation")
        print("==================================================")
        
        # Start the server
        subprocess.run([sys.executable, server_script], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Dreamina server!")
        print(f"💡 Make sure all dependencies are installed:")
        print("   pip install flask requests playwright python-dotenv")
        print(f"💡 Also ensure Playwright browsers are installed:")
        print("   playwright install chromium")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Dreamina server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 