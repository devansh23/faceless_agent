#!/usr/bin/env python3
"""
Simple Dreamina navigation test
"""

import os
import time
from playwright.sync_api import sync_playwright

def test_dreamina_navigation():
    """Simple test to navigate to Dreamina"""
    print("🧪 Testing Dreamina Navigation...")
    
    user_data_dir = os.path.abspath("vpn_browser_session")
    
    try:
        with sync_playwright() as p:
            # Launch browser
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            page = context.new_page()
            
            print("✅ Browser launched")
            
            # Navigate to Dreamina
            print("🌐 Navigating to Dreamina...")
            page.goto("https://dreamina.capcut.com/")
            
            print("✅ Navigation completed")
            print("📄 Current URL:", page.url)
            print("📄 Page title:", page.title())
            
            # Wait a bit and take a screenshot
            time.sleep(5)
            
            # Take screenshot for debugging
            screenshot_path = "dreamina_debug.png"
            page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
            
            # Keep browser open
            print("\n" + "=" * 50)
            print("BROWSER OPEN FOR INSPECTION")
            print("=" * 50)
            print("Please check if Dreamina loaded correctly.")
            print("Press Ctrl+C to close.")
            print("=" * 50)
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived Ctrl+C. Closing...")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dreamina_navigation() 