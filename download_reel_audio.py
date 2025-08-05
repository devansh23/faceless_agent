#!/usr/bin/env python3
"""
Script to download audio files for a specific reel using Google Sheets data
Usage: python3 download_reel_audio.py <reel_number>
"""

import sys
import os
import time
import logging
import requests
from urllib.parse import urlparse, parse_qs
import re
from sheets import get_prompts_by_reel

# Configure logging with more detailed output
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('audio_download.log')
    ]
)
logger = logging.getLogger(__name__)

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

def determine_audio_extension(url, content_type=None):
    """Determine the appropriate audio file extension"""
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

def download_audio_file(url, save_path, audio_number):
    """Download audio file from URL to specified path with improved error handling"""
    try:
        logger.info(f"⬇️  Downloading audio {audio_number}...")
        
        # Handle Google Drive URLs
        if 'drive.google.com' in url:
            file_id = extract_file_id_from_google_drive_url(url)
            if file_id:
                direct_url = get_direct_download_url(file_id)
                logger.info(f"  🔗 Converting Google Drive URL to direct download...")
                logger.info(f"  📁 File ID: {file_id}")
            else:
                logger.error(f"  ❌ Error: Could not extract file ID from Google Drive URL")
                return False
        else:
            direct_url = url
            logger.info(f"  🔗 Using direct URL...")

        # Create session for better download handling
        session = requests.Session()
        
        # First request to get the file
        logger.info(f"  📡 Making download request...")
        response = session.get(direct_url, stream=True, timeout=30)
        
        logger.info(f"  📊 Response status: {response.status_code}")
        logger.info(f"  📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            # Check if it's a Google Drive confirmation page
            if 'drive.google.com' in url and 'text/html' in response.headers.get('content-type', ''):
                logger.info(f"  ⚠️  Got HTML response (likely confirmation page)")
                # Extract the actual download URL from the confirmation page
                content = response.text
                
                # Look for different types of download confirmations
                download_url_match = None
                
                # Pattern 1: Standard Google Drive confirmation
                pattern1 = r'href="([^"]*uc[^"]*export=download[^"]*)"'
                match1 = re.search(pattern1, content)
                if match1:
                    download_url_match = match1.group(1)
                    logger.info(f"  🔍 Found download URL with pattern 1")
                
                # Pattern 2: Alternative confirmation format
                if not download_url_match:
                    pattern2 = r'"(https://drive\.google\.com/uc[^"]*)"'
                    match2 = re.search(pattern2, content)
                    if match2:
                        download_url_match = match2.group(1)
                        logger.info(f"  🔍 Found download URL with pattern 2")
                
                # Pattern 3: Direct download link
                if not download_url_match:
                    pattern3 = r'"(https://drive\.google\.com/file/d/[^"]*)"'
                    match3 = re.search(pattern3, content)
                    if match3:
                        download_url_match = match3.group(1)
                        logger.info(f"  🔍 Found download URL with pattern 3")
                
                if download_url_match:
                    logger.info(f"  🔄 Following confirmation link...")
                    response = session.get(download_url_match, stream=True, timeout=30)
                    logger.info(f"  📊 Second response status: {response.status_code}")
                else:
                    logger.error(f"  ❌ Could not find download URL in confirmation page")
                    return False
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Download the file
            logger.info(f"  💾 Saving to: {save_path}")
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was downloaded
            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                file_size = os.path.getsize(save_path)
                logger.info(f"  ✅ SUCCESS: Audio {audio_number} downloaded ({file_size:,} bytes)")
                return True
            else:
                logger.error(f"  ❌ File was not saved properly")
                return False
                
        else:
            logger.error(f"  ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Download error: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python3 download_reel_audio.py <reel_number>")
        print("Example: python3 download_reel_audio.py 1")
        sys.exit(1)
    
    reel_number = sys.argv[1]
    
    logger.info("=" * 60)
    logger.info("🎵 WhatsApp Reel Audio Download Script")
    logger.info("=" * 60)
    logger.info(f"Starting audio download for reel: {reel_number}")
    
    # Get prompts from Google Sheets (includes audio links)
    try:
        logger.info("📊 Fetching audio data from Google Sheets...")
        prompts = get_prompts_by_reel(reel_number)
        if not prompts:
            logger.error(f"No data found for reel {reel_number}")
            print(f"ERROR: No data found for reel {reel_number}")
            sys.exit(1)
        
        # Extract audio URLs from the prompts data
        audio_data = []
        for prompt_data in prompts:
            # We need to get the audio URL from the sheet
            # Let's modify the sheets.py to include audio URLs
            audio_url = prompt_data.get('audio_url', '')
            if audio_url:
                audio_data.append({
                    'line_no': prompt_data['line_no'],
                    'audio_url': audio_url,
                    'audio_number': len(audio_data) + 1
                })
        
        if not audio_data:
            logger.error(f"No audio URLs found for reel {reel_number}")
            print(f"ERROR: No audio URLs found for reel {reel_number}")
            sys.exit(1)
        
        logger.info(f"✅ Found {len(audio_data)} audio files for reel {reel_number}")
        for i, audio_item in enumerate(audio_data, 1):
            logger.info(f"  🎵 Audio {i}: {audio_item['audio_url'][:50]}...")
            
    except Exception as e:
        logger.error(f"Error fetching audio data from Google Sheets: {e}")
        print(f"ERROR: Failed to fetch audio data - {str(e)}")
        sys.exit(1)
    
    try:
        # Base directory for audio files
        base_dir = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/Audio"
        
        # Track download results
        successful_downloads = 0
        failed_downloads = 0
        total_size_downloaded = 0
        downloaded_files = []
        
        logger.info(f"📁 Audio files will be saved to: {base_dir}")
        
        # Download each audio file
        for audio_item in audio_data:
            audio_number = audio_item['audio_number']
            audio_url = audio_item['audio_url']
            line_no = audio_item['line_no']
            
            # Create filename with audio number
            audio_filename = f"{audio_number}.mp3"
            save_path = os.path.join(base_dir, audio_filename)
            
            logger.info(f"\n🎵 Processing audio {audio_number}/{len(audio_data)} - Line {line_no}...")
            logger.info(f"  🔗 URL: {audio_url}")
            logger.info(f"  📁 Save to: {save_path}")
            logger.info("-" * 40)
            
            # Download the file
            if download_audio_file(audio_url, save_path, audio_number):
                successful_downloads += 1
                file_size = os.path.getsize(save_path)
                total_size_downloaded += file_size
                downloaded_files.append(save_path)
                logger.info(f"  ✅ SUCCESS: Audio {audio_number}")
            else:
                failed_downloads += 1
                logger.info(f"  ❌ FAILED: Audio {audio_number}")
            
            # Small delay between downloads to be respectful
            if audio_number < len(audio_data):  # Don't delay after the last file
                logger.info(f"  ⏳ Waiting 1 second before next download...")
                time.sleep(1)
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 DOWNLOAD SUMMARY")
        logger.info("=" * 50)
        logger.info(f"  ✅ Successful: {successful_downloads}/{len(audio_data)}")
        logger.info(f"  ❌ Failed: {failed_downloads}/{len(audio_data)}")
        logger.info(f"  💾 Total size downloaded: {total_size_downloaded:,} bytes ({total_size_downloaded/1024/1024:.1f} MB)")
        logger.info(f"  📁 Files saved to: {base_dir}")
        
        if successful_downloads > 0:
            logger.info(f"\n🎉 Audio download completed successfully!")
            logger.info("📁 Files saved:")
            for file_path in downloaded_files:
                logger.info(f"  - {file_path}")
            
            print(f"SUCCESS: Downloaded {len(downloaded_files)} audio files for reel {reel_number}")
            sys.exit(0)
        else:
            logger.info(f"\n⚠️  No audio files were downloaded successfully.")
            print(f"ERROR: No audio files downloaded for reel {reel_number}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error during audio download: {e}")
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 