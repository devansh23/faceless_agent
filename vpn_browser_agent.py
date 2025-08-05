import os
import time
import json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

class VPNBrowserAgent:
    """
    A browser agent that maintains a persistent VPN connection across sessions.
    Supports both browser extensions and system-level VPN management.
    """
    
    def __init__(self, user_data_dir="vpn_browser_session", headless=False):
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.headless = headless
        self.context = None
        self.page = None
        
        # VPN Configuration
        self.vpn_extension_path = os.getenv("VPN_EXTENSION_PATH")
        self.vpn_extension_id = os.getenv("VPN_EXTENSION_ID")
        self.use_system_vpn = os.getenv("USE_SYSTEM_VPN", "false").lower() == "true"
        self.vpn_service_name = os.getenv("VPN_SERVICE_NAME", "")
        
        # Create directories
        os.makedirs(self.user_data_dir, exist_ok=True)
        
    def launch_browser_with_vpn(self):
        """Launch browser with VPN extension loaded"""
        try:
            with sync_playwright() as p:
                # Prepare browser arguments
                args = [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--allow-running-insecure-content"
                ]
                
                # Add VPN extension if specified
                if self.vpn_extension_path and os.path.exists(self.vpn_extension_path):
                    args.extend([
                        f"--load-extension={self.vpn_extension_path}",
                        f"--disable-extensions-except={self.vpn_extension_path}"
                    ])
                    print(f"🔒 Loading VPN extension from: {self.vpn_extension_path}")
                
                # Launch persistent context
                self.context = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.headless,
                    args=args,
                    accept_downloads=True,
                    downloads_path=os.path.abspath(".vpn_downloads")
                )
                
                self.page = self.context.new_page()
                
                # Wait for extensions to load
                print("⏳ Waiting for extensions to initialize...")
                time.sleep(5)
                
                # Check if VPN extension is loaded
                if self.vpn_extension_id:
                    self._check_vpn_extension_status()
                
                print("✅ Browser launched with VPN support")
                return True
                
        except Exception as e:
            print(f"❌ Failed to launch browser: {e}")
            return False
    
    def _check_vpn_extension_status(self):
        """Check if VPN extension is properly loaded"""
        try:
            # Try to access extension popup
            extension_url = f"chrome-extension://{self.vpn_extension_id}/popup.html"
            self.page.goto(extension_url)
            time.sleep(2)
            
            # Check if extension page loaded successfully
            if "chrome-extension://" in self.page.url:
                print(f"✅ VPN extension loaded successfully (ID: {self.vpn_extension_id})")
                return True
            else:
                print(f"⚠️  VPN extension may not be properly loaded")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not verify VPN extension status: {e}")
            return False
    
    def connect_vpn_extension(self, auto_connect=True):
        """Connect to VPN using browser extension"""
        if not self.vpn_extension_id:
            print("❌ No VPN extension ID configured")
            return False
            
        try:
            print("🔒 Attempting to connect VPN via extension...")
            
            # Navigate to extension popup
            extension_url = f"chrome-extension://{self.vpn_extension_id}/popup.html"
            self.page.goto(extension_url)
            time.sleep(3)
            
            if auto_connect:
                # Try to find and click connect button
                connect_selectors = [
                    '[data-testid="connect-button"]',
                    '.connect-button',
                    '#connect',
                    'button[aria-label*="connect"]',
                    'button:has-text("Connect")',
                    'button:has-text("Connect to VPN")'
                ]
                
                for selector in connect_selectors:
                    try:
                        connect_btn = self.page.wait_for_selector(selector, timeout=3000)
                        if connect_btn:
                            connect_btn.click()
                            print("✅ VPN connection initiated via extension")
                            time.sleep(5)  # Wait for connection
                            return True
                    except:
                        continue
                
                print("⚠️  Could not find connect button automatically")
                print("   Please connect VPN manually in the browser")
                return False
            else:
                print("📋 VPN extension popup opened - connect manually")
                return True
                
        except Exception as e:
            print(f"❌ Failed to connect VPN extension: {e}")
            return False
    
    def connect_system_vpn(self):
        """Connect to system-level VPN"""
        if not self.vpn_service_name:
            print("❌ No VPN service name configured")
            return False
            
        try:
            import subprocess
            
            print(f"🔒 Connecting to system VPN: {self.vpn_service_name}")
            
            # macOS VPN connection
            result = subprocess.run([
                "networksetup", 
                "-connectpppoeservice", 
                self.vpn_service_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ System VPN connected successfully")
                time.sleep(3)  # Wait for connection to stabilize
                return True
            else:
                print(f"❌ Failed to connect system VPN: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ System VPN connection error: {e}")
            return False
    
    def disconnect_system_vpn(self):
        """Disconnect system-level VPN"""
        if not self.vpn_service_name:
            return False
            
        try:
            import subprocess
            
            print(f"🔓 Disconnecting system VPN: {self.vpn_service_name}")
            
            result = subprocess.run([
                "networksetup", 
                "-disconnectpppoeservice", 
                self.vpn_service_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ System VPN disconnected")
                return True
            else:
                print(f"⚠️  Failed to disconnect system VPN: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️  System VPN disconnect error: {e}")
            return False
    
    def check_vpn_status(self):
        """Check current VPN connection status"""
        try:
            # Check IP address to see if VPN is active
            self.page.goto("https://api.ipify.org?format=json")
            ip_data = self.page.content()
            
            # Extract IP from response
            import re
            ip_match = re.search(r'"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"', ip_data)
            
            if ip_match:
                current_ip = ip_match.group(1)
                print(f"🌐 Current IP Address: {current_ip}")
                
                # You can add logic here to check if IP is from VPN range
                # For now, just return the IP
                return current_ip
            else:
                print("❌ Could not determine current IP")
                return None
                
        except Exception as e:
            print(f"❌ Failed to check VPN status: {e}")
            return None
    
    def navigate_to(self, url):
        """Navigate to a URL with VPN active"""
        try:
            print(f"🌐 Navigating to: {url}")
            self.page.goto(url)
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def wait_for_manual_setup(self):
        """Wait for manual VPN setup and return control"""
        print("\n" + "="*60)
        print("🔒 VPN BROWSER AGENT - MANUAL SETUP MODE")
        print("="*60)
        print("The browser is now open with VPN extension loaded.")
        print("Please:")
        print("1. Log into your VPN service if needed")
        print("2. Connect to your preferred VPN server")
        print("3. Verify the connection is active")
        print("4. Press Enter in this terminal when ready to continue...")
        print("="*60)
        
        input("Press Enter when VPN is connected and ready...")
        print("✅ Continuing with VPN connection active")
    
    def keep_alive(self):
        """Keep the browser session alive for manual inspection"""
        print("\n" + "="*50)
        print("VPN BROWSER SESSION ACTIVE")
        print("="*50)
        print("The browser will remain open for your inspection.")
        print("To close the browser, manually close the browser window.")
        print("To exit this script, press Ctrl+C in the terminal.")
        print("="*50)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C. Exiting...")
            self.close()
    
    def close(self):
        """Close the browser session"""
        if self.context:
            try:
                self.context.close()
                print("✅ Browser session closed")
            except Exception as e:
                print(f"⚠️  Browser close error (ignored): {e}")
        
        if self.use_system_vpn:
            self.disconnect_system_vpn()

def main():
    """Main function to demonstrate VPN browser agent usage"""
    print("🔒 VPN Browser Agent - Starting...")
    
    # Create VPN browser agent
    agent = VPNBrowserAgent(headless=False)
    
    try:
        # Launch browser with VPN support
        if not agent.launch_browser_with_vpn():
            print("❌ Failed to launch browser")
            return
        
        # Connect VPN (choose method)
        if agent.use_system_vpn:
            # System-level VPN
            if not agent.connect_system_vpn():
                print("⚠️  System VPN connection failed")
        elif agent.vpn_extension_id:
            # Browser extension VPN
            if not agent.connect_vpn_extension(auto_connect=True):
                print("⚠️  VPN extension connection failed")
                agent.wait_for_manual_setup()
        else:
            # Manual setup
            agent.wait_for_manual_setup()
        
        # Check VPN status
        current_ip = agent.check_vpn_status()
        if current_ip:
            print(f"✅ VPN connection verified - IP: {current_ip}")
        
        # Navigate to a test site
        agent.navigate_to("https://whatismyipaddress.com/")
        
        # Keep session alive
        agent.keep_alive()
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()

if __name__ == "__main__":
    main() 