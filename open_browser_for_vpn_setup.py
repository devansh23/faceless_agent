#!/usr/bin/env python3
"""
Simple browser launcher for manual VPN setup
"""

import os
import time
from playwright.sync_api import sync_playwright

def open_browser_for_vpn_setup():
    """Open browser for manual VPN setup"""
    print("🔒 Opening browser for VPN setup...")
    print("=" * 50)
    print("Instructions:")
    print("1. Install your preferred VPN extension from Chrome Web Store")
    print("2. Log into your VPN service")
    print("3. Connect to your preferred VPN server")
    print("4. Verify the connection is active")
    print("5. Press Ctrl+C in this terminal when done")
    print("=" * 50)
    
    user_data_dir = os.path.abspath("vpn_browser_session")
    os.makedirs(user_data_dir, exist_ok=True)
    
    try:
        with sync_playwright() as p:
            # Launch browser with basic settings
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
            
            # Navigate to Chrome Web Store for VPN extensions
            print("🌐 Opening Chrome Web Store...")
            page.goto("https://chrome.google.com/webstore/category/extensions")
            
            print("✅ Browser opened successfully!")
            print("📋 Popular VPN extensions you can install:")
            print("   • NordVPN: https://chrome.google.com/webstore/detail/nordvpn-free-vpn-proxy-unblocker/fjoaledfpmneenckfbpohebmkfildcfl")
            print("   • ExpressVPN: https://chrome.google.com/webstore/detail/expressvpn-free-vpn-proxy/bjjchhppbhcheahpgkohchhibcoaocob")
            print("   • ProtonVPN: https://chrome.google.com/webstore/detail/proton-vpn-free-vpn-proxy/plgalgfchbbhnmepmopldpifdjcnkbgh")
            print("   • Windscribe: https://chrome.google.com/webstore/detail/windscribe-free-proxy-and/hnmpcagpplmpfojmgmnngilcnandndhb")
            
            print("\n" + "=" * 50)
            print("🔒 VPN SETUP MODE")
            print("=" * 50)
            print("The browser is now open for you to:")
            print("1. Install VPN extension from Chrome Web Store")
            print("2. Log into your VPN service")
            print("3. Connect to VPN server")
            print("4. Test the connection")
            print("5. Press Ctrl+C when VPN is ready")
            print("=" * 50)
            
            # Keep browser open
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n✅ VPN setup complete!")
                print("🔒 Browser session saved to: vpn_browser_session/")
                print("📝 Next time you run the VPN agent, it will use this session")
                
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    open_browser_for_vpn_setup() 