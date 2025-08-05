#!/usr/bin/env python3
"""
Script to generate multiple images for a reel using WhatsApp/ChatGPT
Usage: python3 generate_reel_images.py <reel_number>
"""

import sys
import os
import time
import shutil
import logging
from playwright.sync_api import sync_playwright
from sheets import get_prompts_by_reel

# Configure logging with more detailed output
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('image_generation.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python3 generate_reel_images.py <reel_number>")
        print("Example: python3 generate_reel_images.py test")
        sys.exit(1)
    
    reel_number = sys.argv[1]
    
    logger.info("=" * 60)
    logger.info("🎨 WhatsApp Reel Image Generation Script")
    logger.info("=" * 60)
    logger.info(f"Starting image generation for reel: {reel_number}")
    
    # Get prompts from Google Sheets
    try:
        logger.info("📊 Fetching prompts from Google Sheets...")
        prompts = get_prompts_by_reel(reel_number)
        if not prompts:
            logger.error(f"No prompts found for reel {reel_number}")
            print(f"ERROR: No prompts found for reel {reel_number}")
            sys.exit(1)
        
        logger.info(f"✅ Found {len(prompts)} prompts for reel {reel_number}")
        for i, prompt_data in enumerate(prompts, 1):
            logger.info(f"  📝 Prompt {i}: {prompt_data['prompt'][:50]}...")
            
    except Exception as e:
        logger.error(f"Error fetching prompts from Google Sheets: {e}")
        print(f"ERROR: Failed to fetch prompts - {str(e)}")
        sys.exit(1)
    
    try:
        whatsapp_url = "https://web.whatsapp.com/"
        chat_name = "ChatGPT"
        user_data_dir = os.path.abspath("whatsapp_session")
        downloads_dir = os.path.abspath(".whatsapp_downloads")
        
        logger.info("🌐 Initializing WhatsApp session...")
        
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir, 
                headless=False, 
                accept_downloads=True, 
                downloads_path=downloads_dir
            )
            page = context.new_page()
            page.goto(whatsapp_url)
            
            # Wait for WhatsApp to load
            chat_selector = f"span[title='{chat_name}']"
            logger.info(f"🔍 Looking for chat: {chat_name}")
            page.wait_for_selector(chat_selector, timeout=120000)
            page.click(chat_selector)
            
            logger.info("✅ WhatsApp session initialized successfully")
            
            # Get message count BEFORE sending any prompts
            messages = page.query_selector_all(".message-in")
            message_count_before_prompts = len(messages)
            logger.info(f"📨 Messages before prompts: {message_count_before_prompts}")
            
            # Send all prompts
            logger.info("🚀 Sending all prompts to ChatGPT...")
            input_box_selector = 'div[contenteditable="true"][data-tab="10"]'
            page.wait_for_selector(input_box_selector, timeout=10000)
            
            for i, prompt_data in enumerate(prompts, 1):
                prompt = prompt_data['prompt']
                logger.info(f"📤 Sending prompt {i}/{len(prompts)}: {prompt[:40]}...")
                
                page.fill(input_box_selector, prompt)
                page.keyboard.press("Enter")
                
                # Small delay between prompts
                time.sleep(2)
            
            logger.info("✅ All prompts sent successfully!")
            
            # Wait 10 minutes for all images to generate
            logger.info("⏰ Waiting 10 minutes for all images to generate...")
            time.sleep(10 * 60)  # 10 minutes
            
            # Get all messages after prompts
            all_messages = page.query_selector_all(".message-in")
            new_messages = all_messages[message_count_before_prompts:]
            logger.info(f"📨 Total new messages after prompts: {len(new_messages)}")
            
            # Find all images in new messages with detailed logging
            image_messages = []
            logger.info("🔍 Scanning for images in new messages...")
            
            for i, bubble in enumerate(new_messages):
                logger.info(f"  🔍 Checking message {i+1}...")
                
                # Try multiple image selectors
                img_selectors = [
                    "img[src^='blob:']",
                    "img[src*='blob']",
                    "img",
                    "img[src]"
                ]
                
                img_elem = None
                for selector in img_selectors:
                    img_elem = bubble.query_selector(selector)
                    if img_elem:
                        logger.info(f"    ✅ Found image with selector: {selector}")
                        break
                
                if img_elem:
                    img_src = img_elem.get_attribute('src')
                    if img_src:
                        logger.info(f"    📸 Image src: {img_src[:50]}...")
                        image_messages.append({
                            'index': i,
                            'src': img_src,
                            'element': img_elem
                        })
                    else:
                        logger.warning(f"    ⚠️  Image element found but no src attribute")
                else:
                    logger.info(f"    ❌ No image found in message {i+1}")
            
            logger.info(f"📊 Found {len(image_messages)} images in new messages")
            
            if len(image_messages) < len(prompts):
                logger.warning(f"⚠️  Expected {len(prompts)} images but found {len(image_messages)}")
                logger.warning(f"⚠️  This might indicate some images failed to generate or weren't detected")
            
            # Download the last N images (where N = number of prompts)
            images_to_download = min(len(image_messages), len(prompts))
            last_images = image_messages[-images_to_download:]
            
            logger.info(f"⬇️  Downloading last {images_to_download} images...")
            
            downloaded_files = []
            for i, img_data in enumerate(last_images):
                try:
                    logger.info(f"  📥 Downloading image {i+1}/{images_to_download}...")
                    
                    # Click on the image to open it
                    img_data['element'].click()
                    time.sleep(1)
                    
                    # Find and click download button
                    download_btn_selector = 'span[data-icon="download-refreshed"]'
                    logger.info(f"    🔍 Looking for download button...")
                    page.wait_for_selector(download_btn_selector, timeout=10000)
                    
                    with page.expect_download() as download_info:
                        page.click(download_btn_selector)
                    
                    download = download_info.value
                    download_path = download.path()
                    logger.info(f"    📁 Downloaded to: {download_path}")
                    
                    # Define save path with image number
                    image_number = i + 1
                    save_path = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/images/{image_number}.png"
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    # Move downloaded file to target location
                    shutil.move(download_path, save_path)
                    downloaded_files.append(save_path)
                    
                    logger.info(f"    ✅ Saved image {image_number}: {save_path}")
                    
                    # Close image view
                    page.keyboard.press("Escape")
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"    ❌ Error downloading image {i+1}: {e}")
            
            logger.info("🎉 SUCCESS: All images generated and downloaded!")
            logger.info(f"📁 Files saved:")
            for file_path in downloaded_files:
                logger.info(f"  - {file_path}")
            
            print(f"SUCCESS: Downloaded {len(downloaded_files)} images for reel {reel_number}")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Error during image generation: {e}")
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 