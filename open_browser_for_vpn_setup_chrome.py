#!/usr/bin/env python3
"""
Browser launcher using system Chrome for VPN extension installation
"""

import os
import subprocess
import time
import platform

def open_system_chrome_for_vpn_setup():
    """Open system Chrome browser for VPN extension installation"""
    print("🔒 Opening system Chrome for VPN setup...")
    print("=" * 60)
    print("This will open your system Chrome browser (not Playwright's Chromium)")
    print("Extension installation will work normally in system Chrome.")
    print("=" * 60)
    
    # Create user data directory for persistent session
    user_data_dir = os.path.abspath("vpn_browser_session")
    os.makedirs(user_data_dir, exist_ok=True)
    
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # Try different Chrome paths on macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium"
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if not chrome_path:
                print("❌ Chrome/Chromium not found. Please install Chrome from:")
                print("   https://www.google.com/chrome/")
                return
            
            # Launch Chrome with user data directory
            cmd = [
                chrome_path,
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "https://chrome.google.com/webstore/category/extensions"
            ]
            
        elif system == "Linux":
            # Try different Chrome paths on Linux
            chrome_paths = [
                "google-chrome",
                "chromium-browser",
                "chromium",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser"
            ]
            
            chrome_path = None
            for path in chrome_paths:
                try:
                    subprocess.run([path, "--version"], capture_output=True, check=True)
                    chrome_path = path
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not chrome_path:
                print("❌ Chrome/Chromium not found. Please install Chrome:")
                print("   sudo apt install google-chrome-stable  # Ubuntu/Debian")
                print("   sudo dnf install google-chrome-stable  # Fedora")
                return
            
            cmd = [
                chrome_path,
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "https://chrome.google.com/webstore/category/extensions"
            ]
            
        elif system == "Windows":
            # Windows Chrome paths
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', ''))
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if not chrome_path:
                print("❌ Chrome not found. Please install Chrome from:")
                print("   https://www.google.com/chrome/")
                return
            
            cmd = [
                chrome_path,
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "https://chrome.google.com/webstore/category/extensions"
            ]
        
        else:
            print(f"❌ Unsupported operating system: {system}")
            return
        
        print(f"🚀 Launching Chrome from: {chrome_path}")
        print("📋 Popular VPN extensions you can install:")
        print("   • NordVPN: https://chrome.google.com/webstore/detail/nordvpn-free-vpn-proxy-unblocker/fjoaledfpmneenckfbpohebmkfildcfl")
        print("   • ExpressVPN: https://chrome.google.com/webstore/detail/expressvpn-free-vpn-proxy/bjjchhppbhcheahpgkohchhibcoaocob")
        print("   • ProtonVPN: https://chrome.google.com/webstore/detail/proton-vpn-free-vpn-proxy/plgalgfchbbhnmepmopldpifdjcnkbgh")
        print("   • Windscribe: https://chrome.google.com/webstore/detail/windscribe-free-proxy-and/hnmpcagpplmpfojmgmnngilcnandndhb")
        
        print("\n" + "=" * 60)
        print("🔒 VPN SETUP MODE")
        print("=" * 60)
        print("Chrome is opening with a dedicated profile for VPN setup.")
        print("Please:")
        print("1. Install your preferred VPN extension from Chrome Web Store")
        print("2. Log into your VPN service")
        print("3. Connect to your preferred VPN server")
        print("4. Test the connection at https://whatismyipaddress.com/")
        print("5. Press Enter in this terminal when VPN is ready")
        print("=" * 60)
        
        # Launch Chrome
        process = subprocess.Popen(cmd)
        
        # Wait for user input
        input("Press Enter when VPN setup is complete...")
        
        # Close Chrome
        print("🔄 Closing Chrome...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("✅ VPN setup complete!")
        print(f"🔒 Browser session saved to: {user_data_dir}")
        print("📝 Next time you run the VPN agent, it will use this session")
        
    except Exception as e:
        print(f"❌ Error launching Chrome: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    open_system_chrome_for_vpn_setup() 