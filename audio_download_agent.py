import os
import requests
import time
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

load_dotenv()

def get_audio_urls_from_sheet():
    """Get audio URLs from Google Sheet 2, Audio File column"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # Open the second worksheet (index 1)
    sheet = client.open_by_key(sheet_id).get_worksheet(1)
    data = sheet.get_all_records()

    audio_urls = []
    for idx, row in enumerate(data, start=1):
        audio_link = row.get("Audio File", "").strip()
        if audio_link:
            audio_urls.append({
                "line_no": str(idx).zfill(3),
                "audio_url": audio_link,
                "reel_no": str(row.get("Reel #", "")).strip()
            })

    return audio_urls

def extract_file_id_from_google_drive_url(url):
    """Extract file ID from various Google Drive URL formats"""
    # Handle different Google Drive URL formats
    if 'drive.google.com' in url:
        if '/file/d/' in url:
            # Format: https://drive.google.com/file/d/FILE_ID/view
            match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        elif 'id=' in url:
            # Format: https://drive.google.com/open?id=FILE_ID
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            return query_params.get('id', [None])[0]
        elif '/uc?' in url:
            # Format: https://drive.google.com/uc?id=FILE_ID
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            return query_params.get('id', [None])[0]
    
    return None

def get_direct_download_url(file_id):
    """Convert Google Drive file ID to direct download URL"""
    return f"https://drive.google.com/uc?id={file_id}&export=download"

def download_audio_file(url, save_path, line_no):
    """Download audio file from URL to specified path with improved error handling"""
    try:
        print(f"⬇️  Downloading audio for line {line_no}...")
        
        # Handle Google Drive URLs
        if 'drive.google.com' in url:
            file_id = extract_file_id_from_google_drive_url(url)
            if file_id:
                direct_url = get_direct_download_url(file_id)
                print(f"  🔗 Converting Google Drive URL to direct download...")
                print(f"  📁 File ID: {file_id}")
            else:
                print(f"  ❌ Error: Could not extract file ID from Google Drive URL")
                return False
        else:
            direct_url = url
            print(f"  🔗 Using direct URL...")

        # Create session for better download handling
        session = requests.Session()
        
        # First request to get the file
        print(f"  📡 Making download request...")
        response = session.get(direct_url, stream=True, timeout=30)
        
        print(f"  📊 Response status: {response.status_code}")
        print(f"  📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            # Check if it's a Google Drive confirmation page
            if 'drive.google.com' in url and 'text/html' in response.headers.get('content-type', ''):
                print(f"  ⚠️  Got HTML response (likely confirmation page)")
                # Extract the actual download URL from the confirmation page
                content = response.text
                
                # Look for different types of download confirmations
                download_url_match = None
                
                # Pattern 1: "Download anyway" link
                if 'Download anyway' in content:
                    print(f"  🔗 Found 'Download anyway' confirmation")
                    download_url_match = re.search(r'href="([^"]*)"[^>]*>Download anyway', content)
                
                # Pattern 2: "Download" button
                elif 'Download' in content and 'href=' in content:
                    print(f"  🔗 Found 'Download' button")
                    download_url_match = re.search(r'href="([^"]*download[^"]*)"', content, re.IGNORECASE)
                
                # Pattern 3: Direct download link
                elif 'export=download' in content:
                    print(f"  🔗 Found direct download link")
                    download_url_match = re.search(r'href="([^"]*export=download[^"]*)"', content)
                
                if download_url_match:
                    download_url = download_url_match.group(1)
                    download_url = download_url.replace('&amp;', '&')
                    print(f"  🔗 Following download link...")
                    response = session.get(download_url, stream=True, timeout=30)
                    response.raise_for_status()
                else:
                    # Check for specific error conditions
                    if 'accounts.google.com' in content or 'signin' in content.lower():
                        print(f"  ❌ File requires Google account sign-in")
                        print(f"  💡 This file is not publicly accessible")
                    elif 'quota' in content.lower():
                        print(f"  ❌ Google Drive quota exceeded")
                    elif 'not found' in content.lower():
                        print(f"  ❌ File not found or deleted")
                    else:
                        print(f"  ❌ No download confirmation found in HTML")
                        print(f"  📄 HTML preview: {content[:200]}...")
                    return False
            else:
                print(f"  ✅ Got direct file response")
            
            # Get file size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Download the file with progress tracking
            print(f"  💾 Saving file to: {save_path}")
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"  📈 Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
            
            # Get final file size
            final_size = os.path.getsize(save_path)
            print(f"  ✅ Downloaded: {save_path}")
            print(f"  📏 File size: {final_size} bytes")
            return True
            
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Download failed for line {line_no}: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ Error downloading line {line_no}: {str(e)}")
        return False

def determine_audio_extension(url, content_type=None):
    """Determine audio file extension from URL or content type"""
    # Try to get extension from URL
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    
    # Common audio extensions
    audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma']
    
    for ext in audio_extensions:
        if path.endswith(ext):
            return ext
    
    # Try to determine from content type
    if content_type:
        if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
            return '.mp3'
        elif 'audio/wav' in content_type:
            return '.wav'
        elif 'audio/mp4' in content_type or 'audio/aac' in content_type:
            return '.m4a'
        elif 'audio/ogg' in content_type:
            return '.ogg'
        elif 'audio/flac' in content_type:
            return '.flac'
    
    # Default to mp3 if we can't determine
    return '.mp3'

def main():
    """Main function to download all audio files with improved reporting"""
    print("🎵 Starting Audio Download Agent...")
    print("=" * 50)
    
    # Get audio URLs from Google Sheet
    print("📊 Reading audio URLs from Google Sheet...")
    audio_data = get_audio_urls_from_sheet()
    
    if not audio_data:
        print("❌ No audio URLs found in the sheet!")
        return
    
    print(f"📋 Found {len(audio_data)} audio files to download")
    print("=" * 50)
    
    # Base directory for audio files
    base_dir = "/Users/devanshc/Documents/cursor projects/n8n_faceless_agent/audio"
    
    # Track download results
    successful_downloads = 0
    failed_downloads = 0
    total_size_downloaded = 0
    
    # Download each audio file
    for i, item in enumerate(audio_data, 1):
        line_no = item['line_no']
        audio_url = item['audio_url']
        reel_no = item['reel_no']
        
        # Create directory structure: audio/1/<audio_number>
        audio_dir = os.path.join(base_dir, "1")
        audio_filename = f"{line_no}{determine_audio_extension(audio_url)}"
        save_path = os.path.join(audio_dir, audio_filename)
        
        print(f"\n🎵 Processing file {i}/{len(audio_data)} - Line {line_no} (Reel {reel_no})...")
        print(f"  🔗 URL: {audio_url}")
        print(f"  📁 Save to: {save_path}")
        print("-" * 40)
        
        # Download the file
        if download_audio_file(audio_url, save_path, line_no):
            successful_downloads += 1
            file_size = os.path.getsize(save_path)
            total_size_downloaded += file_size
            print(f"  ✅ SUCCESS: Line {line_no}")
        else:
            failed_downloads += 1
            print(f"  ❌ FAILED: Line {line_no}")
        
        # Small delay between downloads to be respectful
        if i < len(audio_data):  # Don't delay after the last file
            print(f"  ⏳ Waiting 1 second before next download...")
            time.sleep(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"  ✅ Successful: {successful_downloads}/{len(audio_data)}")
    print(f"  ❌ Failed: {failed_downloads}/{len(audio_data)}")
    print(f"  💾 Total size downloaded: {total_size_downloaded:,} bytes ({total_size_downloaded/1024/1024:.1f} MB)")
    print(f"  📁 Files saved to: {base_dir}/1/")
    
    if successful_downloads > 0:
        print(f"\n🎉 Audio download completed successfully!")
        if failed_downloads > 0:
            print(f"⚠️  Note: {failed_downloads} files failed to download")
    else:
        print(f"\n⚠️  No audio files were downloaded successfully.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 