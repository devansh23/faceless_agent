#!/usr/bin/env python3
"""
Test audio upload to Dreamina using file input selectors
"""

import os
import time
from playwright.sync_api import sync_playwright

def test_audio_upload():
    """Test uploading an audio file to Dreamina using file input selectors"""
    print("🧪 Testing Audio Upload to Dreamina...")
    
    user_data_dir = os.path.abspath("vpn_browser_session")
    
    # Check if we have test audio files
    audio_dir = os.path.abspath("audio")
    if not os.path.exists(audio_dir):
        print("❌ Audio directory not found")
        return
    
    # Find first available audio file
    test_audio = None
    for reel_dir in os.listdir(audio_dir):
        reel_path = os.path.join(audio_dir, reel_dir)
        if os.path.isdir(reel_path):
            for audio_file in os.listdir(reel_path):
                if audio_file.endswith(('.mp3', '.wav', '.m4a', '.aac')):
                    test_audio = os.path.join(reel_path, audio_file)
                    break
            if test_audio:
                break
    
    if not test_audio:
        print("❌ No test audio files found")
        return
    
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
            print("📄 Current URL:", page.url)
            print("📄 Page title:", page.title())
            
            # Test audio upload using the specific audio file input selector
            print("\n🎵 Testing audio upload with audio file input selector...")
            
            # Use the specific selector for audio file inputs
            audio_file_input = page.locator("input[type='file'][accept*='audio']")
            
            # Check if the audio file input exists
            if audio_file_input.count() == 0:
                print("❌ No audio file input found")
                print("🔍 Let's look for all file inputs on the page...")
                
                all_file_inputs = page.query_selector_all('input[type="file"]')
                print(f"📁 Found {len(all_file_inputs)} file input elements")
                
                for i, elem in enumerate(all_file_inputs):
                    try:
                        accept = elem.get_attribute('accept')
                        id_attr = elem.get_attribute('id')
                        class_attr = elem.get_attribute('class')
                        print(f"   File input {i+1}: accept='{accept}', id='{id_attr}', class='{class_attr}'")
                    except:
                        print(f"   File input {i+1}: Could not get details")
                
                return
            
            print(f"✅ Found {audio_file_input.count()} audio file input(s)")
            
            # Get details about the audio file input
            try:
                first_audio_input = audio_file_input.first
                accept = first_audio_input.get_attribute('accept')
                id_attr = first_audio_input.get_attribute('id')
                class_attr = first_audio_input.get_attribute('class')
                print(f"📋 Audio file input: accept='{accept}', id='{id_attr}', class='{class_attr}'")
            except:
                print("📋 Using audio file input")
            
            # Upload the audio file directly using set_input_files
            print("📤 Setting audio file...")
            audio_file_input.set_input_files(test_audio)
            
            # Wait for upload to complete
            time.sleep(3)
            print("✅ Audio upload test completed!")
            
            # Keep browser open for inspection
            print("\n" + "=" * 50)
            print("BROWSER OPEN FOR INSPECTION")
            print("=" * 50)
            print("Please check if the audio was uploaded successfully.")
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
    test_audio_upload()
