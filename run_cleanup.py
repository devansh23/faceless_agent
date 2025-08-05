#!/usr/bin/env python3
"""
Run the cleanup process
"""

import subprocess
import sys
import os

def run_cleanup():
    """Run the cleanup script"""
    try:
        # Run the cleanup script
        result = subprocess.run([sys.executable, 'clear_browser_sessions.py'], 
                              capture_output=True, text=True)
        
        print("🧹 Cleanup Output:")
        print("=" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running cleanup: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting cleanup process...")
    success = run_cleanup()
    
    if success:
        print("\n✅ Cleanup completed successfully!")
        print("💡 Now you can start the improved API server with:")
        print("   python3 simple_http_server.py")
    else:
        print("\n❌ Cleanup failed!") 