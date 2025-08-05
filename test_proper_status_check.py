#!/usr/bin/env python3
"""
Proper status checking: Wait 15 seconds after upload, then check status
"""

import os
import time
from playwright.sync_api import sync_playwright

def test_proper_status_check():
    """Test proper status checking with 15-second wait after upload"""
    print("🧪 Testing Proper Status Check (15s wait after upload)...")
    
    user_data_dir = os.path.abspath("vpn_browser_session")
    
    # Check if we have test files
    images_dir = os.path.abspath("images")
    audio_dir = os.path.abspath("audio")
    
    if not os.path.exists(images_dir) or not os.path.exists(audio_dir):
        print("❌ Images or audio directory not found")
        return
    
    # Find first available image and audio
    test_image = None
    test_audio = None
    
    # Find image
    for reel_dir in os.listdir(images_dir):
        reel_path = os.path.join(images_dir, reel_dir)
        if os.path.isdir(reel_path):
            for img_file in os.listdir(reel_path):
                if img_file.endswith(('.png', '.jpg', '.jpeg')):
                    test_image = os.path.join(reel_path, img_file)
                    break
            if test_image:
                break
    
    # Find audio
    for reel_dir in os.listdir(audio_dir):
        reel_path = os.path.join(audio_dir, reel_dir)
        if os.path.isdir(reel_path):
            for audio_file in os.listdir(reel_path):
                if audio_file.endswith(('.mp3', '.wav', '.m4a', '.aac')):
                    test_audio = os.path.join(reel_path, audio_file)
                    break
            if test_audio:
                break
    
    if not test_image or not test_audio:
        print("❌ Test files not found")
        return
    
    print(f"📁 Using test image: {os.path.basename(test_image)}")
    print(f"📁 Using test audio: {os.path.basename(test_audio)}")
    
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
            
            # Step 1: Upload Image
            print("\n��️  Step 1: Uploading image...")
            
            # Get all file inputs and use the first one (image input)
            all_file_inputs = page.query_selector_all('input[type="file"]')
            
            if len(all_file_inputs) == 0:
                print("❌ No file inputs found")
                return
            
            # Use the first file input (should be for images)
            image_file_input = all_file_inputs[0]
            
            # Upload the image
            print("📤 Setting image file...")
            image_file_input.set_input_files(test_image)
            time.sleep(3)
            print("✅ Image upload completed")
            
            # Step 2: Upload Audio
            print("\n🎵 Step 2: Uploading audio...")
            
            # Use the specific selector for audio file inputs
            audio_file_input = page.locator("input[type='file'][accept*='audio']")
            
            if audio_file_input.count() == 0:
                print("❌ No audio file input found")
                return
            
            # Upload the audio
            print("📤 Setting audio file...")
            audio_file_input.set_input_files(test_audio)
            time.sleep(3)
            print("✅ Audio upload completed")
            
            # Step 3: Press Upload Button
            print("\n⬆️  Step 3: Pressing upload button...")
            
            # Use the exact button class from the HTML
            upload_button_selectors = [
                '.submit-button-bPnDkw',
                '.lv-btn.submit-button-bPnDkw',
                'button.submit-button-bPnDkw',
                'button.lv-btn-primary.submit-button-bPnDkw',
                'button[class*="submit-button-bPnDkw"]',
                'button:has(svg[data-follow-fill="currentColor"])',
                'button.lv-btn-icon-only'
            ]
            
            upload_button = None
            for selector in upload_button_selectors:
                try:
                    upload_button = page.wait_for_selector(selector, timeout=5000)
                    if upload_button:
                        print(f"✅ Found upload button with selector: {selector}")
                        break
                except:
                    continue
            
            if not upload_button:
                print("❌ Could not find upload button")
                return
            
            # Click the upload button
            print("🔄 Clicking upload button...")
            upload_button.click()
            
            # Step 4: Wait 15 seconds for response
            print("\n⏳ Step 4: Waiting 15 seconds for Dreamina response...")
            for i in range(15, 0, -1):
                print(f"   Waiting... {i} seconds remaining")
                time.sleep(1)
            
            # Step 5: Check Status
            print("\n🔍 Step 5: Checking Dreamina status after 15 seconds...")
            
            def check_dreamina_status_after_wait():
                """Check Dreamina's status after the 15-second wait"""
                try:
                    print("🔍 Checking Dreamina status...")
                    
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
            
            # Check status after the wait
            status = check_dreamina_status_after_wait()
            print(f"📊 Final status after 15 seconds: {status}")
            
            if status == 'generating':
                print("🎉 SUCCESS: Dreamina is generating video!")
            elif status == 'error':
                print("❌ ERROR: Upload failed with error!")
            else:
                print("⚠️  UNKNOWN: Could not determine status")
            
            # Keep browser open for inspection
            print("\n" + "=" * 50)
            print("BROWSER OPEN FOR INSPECTION")
            print("=" * 50)
            print("Please check if the status detection was correct.")
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
    test_proper_status_check()
