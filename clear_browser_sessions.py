#!/usr/bin/env python3
"""
Script to clear browser sessions and kill any existing browser processes
"""

import os
import subprocess
import shutil
import time

def kill_browser_processes():
    """Kill any existing browser processes"""
    try:
        # Kill Chrome/Chromium processes
        subprocess.run(['pkill', '-f', 'chrome'], capture_output=True)
        subprocess.run(['pkill', '-f', 'chromium'], capture_output=True)
        subprocess.run(['pkill', '-f', 'Chromium'], capture_output=True)
        print("✅ Killed existing browser processes")
    except Exception as e:
        print(f"⚠️  Error killing processes: {e}")

def clear_session_directories():
    """Clear browser session directories"""
    session_dirs = [
        'whatsapp_session',
        'dreamina_browser_session',
        'vpn_browser_session'
    ]
    
    for session_dir in session_dirs:
        if os.path.exists(session_dir):
            try:
                shutil.rmtree(session_dir)
                print(f"✅ Cleared {session_dir}")
            except Exception as e:
                print(f"⚠️  Error clearing {session_dir}: {e}")

def wait_for_cleanup():
    """Wait a moment for cleanup to complete"""
    print("⏳ Waiting for cleanup to complete...")
    time.sleep(3)

if __name__ == "__main__":
    print("🧹 Clearing browser sessions and processes...")
    print("=" * 50)
    
    kill_browser_processes()
    clear_session_directories()
    wait_for_cleanup()
    
    print("✅ Cleanup complete! You can now restart the API server.")
    print("💡 Run: python3 simple_http_server.py") 