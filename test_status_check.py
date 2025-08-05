#!/usr/bin/env python3
"""
Test status checking functionality
"""

import os
import time
from playwright.sync_api import sync_playwright

def test_status_check():
    """Test the status checking functionality"""
    print("🧪 Testing Status Check Functionality...")
    
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
            
            # Navigate directly to AI Avatar page
            print("🌐 Navigating to Dreamina AI Avatar page...")
            page.goto("https://dreamina.capcut.com/ai-tool/generate?type=digitalHuman")
            
            # Wait for page to load
            time.sleep(5)
            
            print("✅ Navigation completed")
            print("📄 Current URL:", page.url)
            print("📄 Page title:", page.title())
            
            # Test status checking function
            print("\n🔍 Testing status checking...")
            
            def check_dreamina_status(timeout=15):
                """Check Dreamina's status after upload - returns 'generating', 'error', or 'unknown'"""
                try:
                    print("🔍 Checking Dreamina status...")
                    
                    # Wait for response
                    time.sleep(3)
                    
                    # Look for various status indicators
                    status_indicators = {
                        'generating': [
                            'text=generating',
                            'text=processing',
                            'text=creating',
                            'text=video',
                            'text=progress',
                            '[class*="progress"]',
                            '[class*="loading"]',
                            '[class*="spinner"]'
                        ],
                        'error': [
                            'text=too many people',
                            'text=error',
                            'text=failed',
                            'text=unavailable',
                            'text=try again',
                            'text=retry',
                            '[class*="error"]',
                            '[class*="failed"]'
                        ]
                    }
                    
                    # Check for generating indicators
                    for indicator in status_indicators['generating']:
                        try:
                            element = page.wait_for_selector(indicator, timeout=2000)
                            if element:
                                print(f"✅ Found generating indicator: {indicator}")
                                return 'generating'
                        except:
                            continue
                    
                    # Check for error indicators
                    for indicator in status_indicators['error']:
                        try:
                            element = page.wait_for_selector(indicator, timeout=2000)
                            if element:
                                error_text = element.evaluate('el => el.textContent')
                                print(f"❌ Found error indicator: {indicator} - '{error_text}'")
                                return 'error'
                        except:
                            continue
                    
                    # If no specific indicators found, check page content
                    page_content = page.content().lower()
                    
                    if any(phrase in page_content for phrase in ['generating', 'processing', 'creating', 'progress']):
                        print("✅ Page content suggests generating")
                        return 'generating'
                    
                    if any(phrase in page_content for phrase in ['too many people', 'error', 'failed', 'unavailable', 'try again']):
                        print("❌ Page content suggests error")
                        return 'error'
                    
                    print("⚠️  Could not determine status")
                    return 'unknown'
                    
                except Exception as e:
                    print(f"❌ Error checking status: {e}")
                    return 'unknown'
            
            # Test current page status
            status = check_dreamina_status()
            print(f"📊 Current page status: {status}")
            
            # Keep browser open for inspection
            print("\n" + "=" * 50)
            print("BROWSER OPEN FOR INSPECTION")
            print("=" * 50)
            print("Please check the page and see what status indicators are present.")
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
    test_status_check()
