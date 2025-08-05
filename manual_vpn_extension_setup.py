#!/usr/bin/env python3
"""
Manual VPN extension setup helper
"""

import os
import requests
import zipfile
import json
from pathlib import Path

def download_vpn_extension_manual():
    """Manual VPN extension download and setup"""
    print("🔧 Manual VPN Extension Setup")
    print("=" * 50)
    print("Since Chrome Web Store doesn't allow direct downloads,")
    print("we'll help you set up the extension manually.")
    print("=" * 50)
    
    # Create extensions directory
    extensions_dir = Path("vpn_extensions")
    extensions_dir.mkdir(exist_ok=True)
    
    print("📋 Available VPN Extensions:")
    print("1. NordVPN")
    print("2. ExpressVPN") 
    print("3. ProtonVPN")
    print("4. Windscribe")
    print("5. Custom extension")
    
    choice = input("\nSelect extension (1-5): ").strip()
    
    extension_info = {
        "1": {"name": "nordvpn", "display": "NordVPN"},
        "2": {"name": "expressvpn", "display": "ExpressVPN"},
        "3": {"name": "protonvpn", "display": "ProtonVPN"},
        "4": {"name": "windscribe", "display": "Windscribe"},
        "5": {"name": "custom", "display": "Custom"}
    }
    
    if choice not in extension_info:
        print("❌ Invalid choice")
        return
    
    selected = extension_info[choice]
    
    if selected["name"] == "custom":
        extension_name = input("Enter extension name: ").strip()
        extension_path = input("Enter path to extracted extension folder: ").strip()
    else:
        extension_name = selected["name"]
        extension_path = input(f"Enter path to extracted {selected['display']} extension folder: ").strip()
    
    # Validate path
    if not os.path.exists(extension_path):
        print(f"❌ Path not found: {extension_path}")
        return
    
    # Copy to our extensions directory
    target_dir = extensions_dir / extension_name
    if target_dir.exists():
        import shutil
        shutil.rmtree(target_dir)
    
    import shutil
    shutil.copytree(extension_path, target_dir)
    
    print(f"✅ Extension copied to: {target_dir}")
    
    # Extract extension ID
    manifest_path = target_dir / "manifest.json"
    if not manifest_path.exists():
        print("❌ manifest.json not found in extension directory")
        return
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Try to get extension ID
        extension_id = None
        
        # Method 1: From key field
        key = manifest.get('key')
        if key:
            extension_id = key.split('__')[0]
        
        # Method 2: From name
        if not extension_id:
            name = manifest.get('name', '').lower().replace(' ', '')
            if name:
                extension_id = name
        
        # Method 3: Manual input
        if not extension_id:
            print("⚠️  Could not determine extension ID automatically")
            extension_id = input("Please enter the extension ID manually: ").strip()
        
        if not extension_id:
            print("❌ No extension ID provided")
            return
        
        print(f"✅ Extension ID: {extension_id}")
        
        # Update .env file
        update_env_file(str(target_dir), extension_id)
        
        print("\n🎉 Manual extension setup complete!")
        print(f"📁 Extension path: {target_dir}")
        print(f"🆔 Extension ID: {extension_id}")
        print("🔒 You can now run the VPN agent with this extension")
        
    except Exception as e:
        print(f"❌ Error processing extension: {e}")

def update_env_file(extension_path, extension_id):
    """Update .env file with extension settings"""
    env_file = Path(".env")
    
    # Read existing .env file
    env_lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add VPN settings
    vpn_settings = {
        "VPN_EXTENSION_PATH": extension_path,
        "VPN_EXTENSION_ID": extension_id,
        "USE_SYSTEM_VPN": "false"
    }
    
    # Update existing lines or add new ones
    updated_lines = []
    existing_keys = set()
    
    for line in env_lines:
        key = line.split('=')[0] if '=' in line else None
        if key in vpn_settings:
            updated_lines.append(f"{key}={vpn_settings[key]}\n")
            existing_keys.add(key)
        else:
            updated_lines.append(line)
    
    # Add missing settings
    for key, value in vpn_settings.items():
        if key not in existing_keys:
            updated_lines.append(f"{key}={value}\n")
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Updated .env file with VPN settings")

def provide_manual_instructions():
    """Provide manual extension installation instructions"""
    print("\n📋 Manual Extension Installation Instructions")
    print("=" * 60)
    print("If you can't install extensions in the browser, follow these steps:")
    print()
    print("1. Open your regular Chrome browser (not the automated one)")
    print("2. Go to Chrome Web Store and install your preferred VPN extension")
    print("3. Find the extension in Chrome's extension management page:")
    print("   chrome://extensions/")
    print("4. Enable 'Developer mode' (toggle in top right)")
    print("5. Click 'Pack extension' and note the extension ID")
    print("6. Or manually extract the extension files:")
    print("   - Find extension in: ~/Library/Application Support/Google/Chrome/Default/Extensions/")
    print("   - Copy the extension folder to vpn_extensions/")
    print()
    print("7. Run this script again to configure the extension")
    print("=" * 60)

if __name__ == "__main__":
    print("🔧 VPN Extension Setup Options")
    print("=" * 40)
    print("1. Manual extension setup")
    print("2. View manual installation instructions")
    
    choice = input("\nSelect option (1-2): ").strip()
    
    if choice == "1":
        download_vpn_extension_manual()
    elif choice == "2":
        provide_manual_instructions()
    else:
        print("❌ Invalid choice") 