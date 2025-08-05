#!/usr/bin/env python3
"""
Dreamina Browser Session Launcher
Opens a persistent browser session for Dreamina login and automation
"""

import os
import time
from playwright.sync_api import sync_playwright

def open_dreamina_session():
    """Open persistent browser session for Dreamina"""
    print("🎬 Opening Dreamina Browser Session...")
    print("=" * 60)
    print("This will open a browser with your VPN session loaded")
    print("and navigate to Dreamina for login and setup.")
    print("=" * 60)
    
    # Use the same user data directory as VPN setup
    user_data_dir = os.path.abspath("vpn_browser_session")
    downloads_dir = os.path.abspath(".dreamina_downloads")
    
    # Create directories
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(downloads_dir, exist_ok=True)
    
    try:
        with sync_playwright() as p:
            # Launch browser with VPN session
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                accept_downloads=True,
                downloads_path=downloads_dir,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--allow-running-insecure-content"
                ]
            )
            
            page = context.new_page()
            
            print("🌐 Navigating to Dreamina...")
            page.goto("https://dreamina.capcut.com/")
            
            print("✅ Dreamina loaded successfully!")
            print("\n" + "=" * 60)
            print("🎬 DREAMINA SETUP MODE")
            print("=" * 60)
            print("Please:")
            print("1. Log into your Dreamina account")
            print("2. Navigate to the upload/creation section")
            print("3. Familiarize yourself with the interface")
            print("4. Test uploading a sample image and audio file")
            print("5. Note the upload process and any required steps")
            print("6. Press Ctrl+C when ready to proceed with automation")
            print("=" * 60)
            
            # Keep browser open
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n✅ Dreamina session setup complete!")
                print("🔒 Browser session saved to: vpn_browser_session/")
                print("📝 Login and settings will persist for automation")
                print("🎬 Ready to create Dreamina upload automation agent")
                
    except Exception as e:
        print(f"❌ Error opening Dreamina session: {e}")
        import traceback
        traceback.print_exc()

def test_dreamina_upload_flow():
    """Test the Dreamina upload flow to understand the process"""
    print("\n🧪 Dreamina Upload Flow Analysis")
    print("=" * 50)
    print("While you're logged into Dreamina, please:")
    print()
    print("1. Go to the upload/create section")
    print("2. Try uploading a test image file")
    print("3. Try uploading a test audio file")
    print("4. Note the file upload selectors and process")
    print("5. Check if there are any form fields to fill")
    print("6. Observe the submission process")
    print("7. Note any success/error messages")
    print()
    print("This will help us create the automation agent.")
    print("=" * 50)

if __name__ == "__main__":
    print("🎬 Dreamina Session Options")
    print("=" * 40)
    print("1. Open Dreamina browser session")
    print("2. View upload flow analysis guide")
    
    choice = input("\nSelect option (1-2): ").strip()
    
    if choice == "1":
        open_dreamina_session()
    elif choice == "2":
        test_dreamina_upload_flow()
    else:
        print("❌ Invalid choice")
        print("Opening Dreamina session by default...")
        open_dreamina_session() 