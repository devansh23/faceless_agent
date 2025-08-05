#!/usr/bin/env python3
"""
Test image upload to Dreamina using file input selectors
"""

import os
import time
from playwright.sync_api import sync_playwright

def test_image_upload():
    """Test uploading an image to Dreamina using file input selectors"""
    print("🧪 Testing Image Upload to Dreamina...")
    
    user_data_dir = os.path.abspath("vpn_browser_session")
    
    # Check if we have test images
    images_dir = os.path.abspath("images")
    if not os.path.exists(images_dir):
        print("❌ Images directory not found")
        return
    
    # Find first available image
    test_image = None
    for reel_dir in os.listdir(images_dir):
        reel_path = os.path.join(images_dir, reel_dir)
        if os.path.isdir(reel_path):
            for img_file in os.listdir(reel_path):
                if img_file.endswith(('.png', '.jpg', '.jpeg')):
                    test_image = os.path.join(reel_path, img_file)
                    break
            if test_image:
                break
    
    if not test_image:
        print("❌ No test images found")
        return
    
    print(f"📁 Using test image: {os.path.basename(test_image)}")
    
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
            
            # Test image upload by getting all file inputs and using the first one
            print("\n🖼️  Testing image upload by targeting first file input...")
            
            # Get all file inputs
            all_file_inputs = page.query_selector_all('input[type="file"]')
            print(f"📁 Found {len(all_file_inputs)} file input elements")
            
            if len(all_file_inputs) == 0:
                print("❌ No file inputs found")
                return
            
            # Use the first file input (should be for images)
            file_input = all_file_inputs[0]
            
            # Get details about the file input
            try:
                accept = file_input.get_attribute('accept')
                id_attr = file_input.get_attribute('id')
                class_attr = file_input.get_attribute('class')
                print(f"📋 Using file input: accept='{accept}', id='{id_attr}', class='{class_attr}'")
            except:
                print("📋 Using first file input")
            
            # Upload the image directly using set_input_files
            print("📤 Setting image file...")
            file_input.set_input_files(test_image)
            
            # Wait for upload to complete
            time.sleep(3)
            print("✅ Image upload test completed!")
            
            # Keep browser open for inspection
            print("\n" + "=" * 50)
            print("BROWSER OPEN FOR INSPECTION")
            print("=" * 50)
            print("Please check if the image was uploaded successfully.")
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
    test_image_upload()
