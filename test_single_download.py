import os
import requests
import re
from urllib.parse import urlparse, parse_qs

def extract_file_id_from_google_drive_url(url):
    """Extract file ID from various Google Drive URL formats"""
    if 'drive.google.com' in url:
        if '/file/d/' in url:
            match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
    return None

def get_direct_download_url(file_id):
    """Convert Google Drive file ID to direct download URL"""
    return f"https://drive.google.com/uc?id={file_id}&export=download"

def download_file(url, save_path):
    """Download file from Google Drive URL"""
    try:
        print(f"Testing download for: {url}")
        
        # Extract file ID
        file_id = extract_file_id_from_google_drive_url(url)
        if not file_id:
            print("❌ Could not extract file ID from URL")
            return False
        
        print(f"📁 File ID: {file_id}")
        
        # Get direct download URL
        direct_url = get_direct_download_url(file_id)
        print(f"🔗 Direct URL: {direct_url}")
        
        # Create session
        session = requests.Session()
        
        # Try to download
        print("⬇️  Attempting download...")
        response = session.get(direct_url, stream=True, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            # Check if it's a confirmation page
            if 'text/html' in response.headers.get('content-type', ''):
                print("⚠️  Got HTML response (likely confirmation page)")
                content = response.text
                
                # Look for download confirmation
                if 'Download anyway' in content:
                    print("✅ Found 'Download anyway' link")
                    download_url_match = re.search(r'href="([^"]*)"[^>]*>Download anyway', content)
                    if download_url_match:
                        download_url = download_url_match.group(1)
                        download_url = download_url.replace('&amp;', '&')
                        print(f"🔗 Following download link: {download_url}")
                        
                        response = session.get(download_url, stream=True, timeout=30)
                        response.raise_for_status()
                else:
                    print("❌ No download confirmation found in HTML")
                    print("📄 HTML preview:", content[:500])
                    return False
            else:
                print("✅ Got direct file response")
            
            # Save the file
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ File saved to: {save_path}")
            return True
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the specific file
    test_url = "https://drive.google.com/file/d/15ACRk9dryUrQFJLqNGPDZtDLIH1n74rC/view?usp=sharing"
    save_path = "./test_download.mp3"  # Fixed: Added explicit path
    
    print("🧪 Testing single file download...")
    success = download_file(test_url, save_path)
    
    if success:
        print(f"\n🎉 Download successful! File saved as: {save_path}")
        print(f"📁 File location: {os.path.abspath(save_path)}")
        print(f"💾 File size: {os.path.getsize(save_path)} bytes")
    else:
        print(f"\n❌ Download failed. This might be due to:")
        print("   - File requires specific authentication")
        print("   - File is not publicly accessible")
        print("   - File requires Google account sign-in") 