#!/usr/bin/env python3
"""
Improved status checking with better error detection
"""

import os
import time
from playwright.sync_api import sync_playwright

def test_improved_status_check():
    """Test improved status checking with better error detection"""
    print("🧪 Testing Improved Status Check...")
    
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
            
            # Test improved status checking function
            print("\n🔍 Testing improved status checking...")
            
            def check_dreamina_status_improved(timeout=15):
                """Improved status checking with better error detection"""
                try:
                    print("🔍 Checking Dreamina status...")
                    
                    # Wait for response
                    time.sleep(3)
                    
                    # Look for various status indicators with more specific patterns
                    status_indicators = {
                        'generating': [
                            'text=generating',
                            'text=processing',
                            'text=creating',
                            'text=progress',
                            '[class*="progress"]',
                            '[class*="loading"]',
                            '[class*="spinner"]'
                        ],
                        'error': [
                            'text=too many people',
                            'text=a lot of people',
                            'text=applying lip sync',
                            'text=try again later',
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
                    
                    # If no specific indicators found, check page content more thoroughly
                    page_content = page.content().lower()
                    
                    # Check for specific error phrases
                    error_phrases = [
                        'too many people',
                        'a lot of people',
                        'applying lip sync',
                        'try again later',
                        'error',
                        'failed',
                        'unavailable'
                    ]
                    
                    for phrase in error_phrases:
                        if phrase in page_content:
                            print(f"❌ Found error phrase in page content: '{phrase}'")
                            return 'error'
                    
                    # Check for generating phrases
                    generating_phrases = [
                        'generating',
                        'processing',
                        'creating',
                        'progress'
                    ]
                    
                    for phrase in generating_phrases:
                        if phrase in page_content:
                            print(f"✅ Found generating phrase in page content: '{phrase}'")
                            return 'generating'
                    
                    print("⚠️  Could not determine status")
                    return 'unknown'
                    
                except Exception as e:
                    print(f"❌ Error checking status: {e}")
                    return 'unknown'
            
            # Test current page status
            status = check_dreamina_status_improved()
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
    test_improved_status_check()
