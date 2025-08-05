#!/usr/bin/env python3
"""
Test script for VPN Browser Agent
"""

import os
import time
from vpn_browser_agent import VPNBrowserAgent
from dotenv import load_dotenv

load_dotenv()

def test_vpn_agent():
    """Test the VPN browser agent functionality"""
    print("🧪 Testing VPN Browser Agent...")
    
    # Create agent
    agent = VPNBrowserAgent(headless=False)
    
    try:
        # Test 1: Launch browser
        print("\n📋 Test 1: Launching browser with VPN support...")
        if not agent.launch_browser_with_vpn():
            print("❌ Browser launch failed")
            return False
        print("✅ Browser launched successfully")
        
        # Test 2: Check VPN status
        print("\n📋 Test 2: Checking VPN status...")
        current_ip = agent.check_vpn_status()
        if current_ip:
            print(f"✅ IP check successful: {current_ip}")
        else:
            print("⚠️  Could not determine IP address")
        
        # Test 3: Navigate to test site
        print("\n📋 Test 3: Testing navigation...")
        if agent.navigate_to("https://whatismyipaddress.com/"):
            print("✅ Navigation successful")
        else:
            print("❌ Navigation failed")
        
        # Test 4: Manual VPN setup (if needed)
        print("\n📋 Test 4: VPN setup mode...")
        print("   This will open the browser for manual VPN setup")
        print("   Press Enter to continue or Ctrl+C to skip...")
        
        try:
            input("Press Enter to continue...")
            agent.wait_for_manual_setup()
        except KeyboardInterrupt:
            print("   Skipping manual setup...")
        
        # Test 5: Final IP check
        print("\n📋 Test 5: Final VPN status check...")
        final_ip = agent.check_vpn_status()
        if final_ip:
            print(f"✅ Final IP: {final_ip}")
            if current_ip and final_ip != current_ip:
                print("🎉 IP address changed - VPN may be active!")
            else:
                print("ℹ️  IP address unchanged")
        else:
            print("⚠️  Could not determine final IP")
        
        # Keep session alive for inspection
        print("\n📋 Test 6: Keeping session alive...")
        print("   Browser will stay open for manual inspection")
        print("   Press Ctrl+C to close...")
        agent.keep_alive()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        agent.close()
    
    return True

def test_extension_setup():
    """Test VPN extension setup"""
    print("\n🔧 Testing VPN Extension Setup...")
    
    from vpn_config import VPNConfig
    config = VPNConfig()
    
    # List available extensions
    config.list_available_extensions()
    
    # Test extension ID extraction
    print("\n📋 Testing extension ID extraction...")
    test_manifest = {
        "name": "Test VPN Extension",
        "version": "1.0.0",
        "key": "test_extension_id__some_random_string"
    }
    
    import tempfile
    import json
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_path = os.path.join(temp_dir, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(test_manifest, f)
        
        extension_id = config.extract_extension_id(temp_dir)
        if extension_id == "test_extension_id":
            print("✅ Extension ID extraction working")
        else:
            print(f"❌ Extension ID extraction failed: got {extension_id}")

def main():
    """Main test function"""
    print("🔒 VPN Browser Agent - Test Suite")
    print("=" * 40)
    
    # Check environment
    print("📋 Environment Check:")
    vpn_extension_path = os.getenv("VPN_EXTENSION_PATH")
    vpn_extension_id = os.getenv("VPN_EXTENSION_ID")
    use_system_vpn = os.getenv("USE_SYSTEM_VPN", "false")
    
    print(f"   VPN Extension Path: {vpn_extension_path or 'Not set'}")
    print(f"   VPN Extension ID: {vpn_extension_id or 'Not set'}")
    print(f"   Use System VPN: {use_system_vpn}")
    
    if not vpn_extension_path and not use_system_vpn == "true":
        print("\n⚠️  No VPN configuration found")
        print("   Run: python vpn_config.py setup <extension_name>")
        print("   Or set USE_SYSTEM_VPN=true in .env file")
    
    # Run tests
    print("\n" + "=" * 40)
    print("🧪 Running Tests...")
    
    # Test extension setup
    test_extension_setup()
    
    # Test VPN agent
    success = test_vpn_agent()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("❌ Some tests failed")
    
    print("=" * 40)

if __name__ == "__main__":
    main() 