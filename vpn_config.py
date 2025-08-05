"""
VPN Configuration and Extension Management
"""

import os
import json
import zipfile
import requests
from pathlib import Path

class VPNConfig:
    """Configuration management for VPN browser agent"""
    
    def __init__(self):
        self.extensions_dir = Path("vpn_extensions")
        self.extensions_dir.mkdir(exist_ok=True)
        
    def get_extension_info(self, extension_name):
        """Get extension information for popular VPN services"""
        extensions = {
            "nordvpn": {
                "name": "NordVPN",
                "chrome_store_id": "fjoaledfpmneenckfbpohebmkfildcfl",
                "manifest_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                "popup_path": "popup.html"
            },
            "expressvpn": {
                "name": "ExpressVPN",
                "chrome_store_id": "bjjchhppbhcheahpgkohchhibcoaocob",
                "manifest_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                "popup_path": "popup.html"
            },
            "protonvpn": {
                "name": "ProtonVPN",
                "chrome_store_id": "plgalgfchbbhnmepmopldpifdjcnkbgh",
                "manifest_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                "popup_path": "popup.html"
            },
            "windscribe": {
                "name": "Windscribe",
                "chrome_store_id": "hnmpcagpplmpfojmgmnngilcnandndhb",
                "manifest_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                "popup_path": "popup.html"
            }
        }
        return extensions.get(extension_name.lower())
    
    def download_extension(self, extension_name):
        """Download extension from Chrome Web Store"""
        extension_info = self.get_extension_info(extension_name)
        if not extension_info:
            print(f"❌ Unknown extension: {extension_name}")
            return None
            
        extension_dir = self.extensions_dir / extension_name
        extension_dir.mkdir(exist_ok=True)
        
        print(f"📥 Downloading {extension_info['name']} extension...")
        
        # Note: Chrome Web Store doesn't allow direct downloads
        # This is a placeholder for manual download instructions
        print(f"⚠️  Manual download required for {extension_info['name']}")
        print(f"   1. Go to: https://chrome.google.com/webstore/detail/{extension_info['chrome_store_id']}")
        print(f"   2. Download the .crx file")
        print(f"   3. Extract it to: {extension_dir}")
        print(f"   4. Update your .env file with:")
        print(f"      VPN_EXTENSION_PATH={extension_dir}")
        print(f"      VPN_EXTENSION_ID=<extract_from_manifest.json>")
        
        return extension_dir
    
    def extract_extension_id(self, extension_path):
        """Extract extension ID from manifest.json"""
        try:
            manifest_path = Path(extension_path) / "manifest.json"
            if not manifest_path.exists():
                print(f"❌ Manifest not found at: {manifest_path}")
                return None
                
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Try to get key from manifest
            key = manifest.get('key')
            if key:
                # Extract ID from key (first part before __)
                extension_id = key.split('__')[0]
                return extension_id
            
            # Fallback: try to get from name or other fields
            name = manifest.get('name', '').lower().replace(' ', '')
            if name:
                return name
                
            print("⚠️  Could not extract extension ID from manifest")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting extension ID: {e}")
            return None
    
    def setup_extension(self, extension_name):
        """Complete setup for a VPN extension"""
        print(f"🔧 Setting up {extension_name} extension...")
        
        # Download/extract extension
        extension_dir = self.download_extension(extension_name)
        if not extension_dir:
            return False
        
        # Extract extension ID
        extension_id = self.extract_extension_id(extension_dir)
        if not extension_id:
            print("⚠️  Could not determine extension ID")
            print("   Please check the manifest.json file manually")
            return False
        
        print(f"✅ Extension setup complete:")
        print(f"   Path: {extension_dir}")
        print(f"   ID: {extension_id}")
        
        # Update environment variables
        self.update_env_file(extension_dir, extension_id)
        
        return True
    
    def update_env_file(self, extension_path, extension_id):
        """Update .env file with VPN extension settings"""
        env_file = Path(".env")
        
        # Read existing .env file
        env_lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add VPN settings
        vpn_settings = {
            "VPN_EXTENSION_PATH": str(extension_path),
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
    
    def list_available_extensions(self):
        """List all available VPN extensions"""
        print("📋 Available VPN Extensions:")
        print("=" * 40)
        
        extensions = [
            "nordvpn",
            "expressvpn", 
            "protonvpn",
            "windscribe"
        ]
        
        for ext in extensions:
            info = self.get_extension_info(ext)
            if info:
                print(f"• {info['name']} ({ext})")
        
        print("\nTo setup an extension, run:")
        print("python vpn_config.py setup <extension_name>")

def main():
    """Main function for VPN configuration"""
    import sys
    
    config = VPNConfig()
    
    if len(sys.argv) < 2:
        print("🔧 VPN Configuration Tool")
        print("=" * 30)
        print("Usage:")
        print("  python vpn_config.py list                    # List available extensions")
        print("  python vpn_config.py setup <extension_name>  # Setup specific extension")
        print("  python vpn_config.py extract <path>          # Extract extension ID from path")
        print()
        config.list_available_extensions()
        return
    
    command = sys.argv[1]
    
    if command == "list":
        config.list_available_extensions()
    
    elif command == "setup":
        if len(sys.argv) < 3:
            print("❌ Please specify extension name")
            print("   Example: python vpn_config.py setup nordvpn")
            return
        
        extension_name = sys.argv[2]
        config.setup_extension(extension_name)
    
    elif command == "extract":
        if len(sys.argv) < 3:
            print("❌ Please specify extension path")
            print("   Example: python vpn_config.py extract ./vpn_extensions/nordvpn")
            return
        
        extension_path = sys.argv[2]
        extension_id = config.extract_extension_id(extension_path)
        if extension_id:
            print(f"✅ Extension ID: {extension_id}")
        else:
            print("❌ Could not extract extension ID")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use 'list', 'setup', or 'extract'")

if __name__ == "__main__":
    main() 