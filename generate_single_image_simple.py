#!/usr/bin/env python3
"""
Simple script to generate a single image using WhatsApp/ChatGPT
Usage: python3 generate_single_image_simple.py <reel_number> <snippet_number> <image_prompt>
"""

import sys
import os
import time
import shutil
import logging
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    if len(sys.argv) != 4:
        print("Usage: python3 generate_single_image_simple.py <reel_number> <snippet_number> <image_prompt>")
        print("Example: python3 generate_single_image_simple.py test 001 'A simple red circle on white background'")
        sys.exit(1)
    
    reel_number = sys.argv[1]
    snippet_number = sys.argv[2]
    image_prompt = sys.argv[3]
    
    logger.info("=" * 60)
    logger.info("🎨 WhatsApp Image Generation Script")
    logger.info("=" * 60)
    logger.info(f"Starting image generation for reel={reel_number}, snippet={snippet_number}")
    logger.info(f"Prompt: {image_prompt}")
    
    try:
        whatsapp_url = "https://web.whatsapp.com/"
        chat_name = "ChatGPT"
        user_data_dir = os.path.abspath("whatsapp_session")
        downloads_dir = os.path.abspath(".whatsapp_downloads")
        
        logger.info("Initializing WhatsApp session...")
        
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
            page.wait_for_selector(chat_selector, timeout=120000)
            page.click(chat_selector)
            
            logger.info("WhatsApp session initialized successfully")
            
            # Get message count BEFORE sending the prompt
            messages = page.query_selector_all(".message-in")
            message_count_before_prompt = len(messages)
            logger.info(f"Messages before prompt: {message_count_before_prompt}")
            
            # Send the prompt
            input_box_selector = 'div[contenteditable="true"][data-tab="10"]'
            page.wait_for_selector(input_box_selector, timeout=10000)
            page.fill(input_box_selector, image_prompt)
            page.keyboard.press("Enter")
            logger.info(f"Successfully sent prompt: {image_prompt[:40]}...")
            
            # Wait for image generation
            logger.info("Waiting for image generation (timeout: 10 minutes)...")
            start_time = time.time()
            timeout_seconds = 10 * 60  # 10 minutes
            
            img_src = None
            while time.time() - start_time < timeout_seconds:
                # Get all messages
                all_messages = page.query_selector_all(".message-in")
                total_messages = len(all_messages)
                
                # Only consider messages that appeared AFTER we sent the prompt
                new_messages = all_messages[message_count_before_prompt:]
                logger.info(f"Total messages: {total_messages}, New messages after prompt: {len(new_messages)}")
                
                # Look for new images in new messages only
                for i, bubble in enumerate(new_messages):
                    img_elem = bubble.query_selector("img[src^='blob:']")
                    if img_elem:
                        img_src = img_elem.get_attribute('src')
                        if img_src:
                            logger.info(f"Image found in new message {message_count_before_prompt + i + 1}")
                            break
                
                if img_src:
                    break
                
                # Check for error messages in new messages
                for i, bubble in enumerate(new_messages):
                    error_indicators = [
                        "Sorry, I can't generate that image",
                        "I'm unable to create this image",
                        "Error generating image",
                        "Unable to process",
                        "Sorry, I can't do that"
                    ]
                    
                    message_text = bubble.inner_text().lower()
                    for indicator in error_indicators:
                        if indicator.lower() in message_text:
                            logger.error(f"Error detected in new message {message_count_before_prompt + i + 1}: {indicator}")
                            print("ERROR: Image generation failed - error detected in response")
                            sys.exit(1)
                
                time.sleep(30)  # Check every 30 seconds
                elapsed_minutes = int((time.time() - start_time) / 60)
                logger.info(f"Still waiting... ({elapsed_minutes}/10 minutes elapsed)")
            
            if not img_src:
                logger.error("Timeout reached after 10 minutes")
                print("ERROR: Image generation timed out")
                sys.exit(1)
            
            # Download the image
            logger.info("Downloading image...")
            img_elem = page.query_selector(f"img[src='{img_src}']")
            if not img_elem:
                logger.error(f"Image not found with src {img_src}")
                print("ERROR: Image not found")
                sys.exit(1)
            
            img_elem.click()
            download_btn_selector = 'span[data-icon="download-refreshed"]'
            page.wait_for_selector(download_btn_selector, timeout=20000)
            
            with page.expect_download() as download_info:
                page.click(download_btn_selector)
            
            download = download_info.value
            download_path = download.path()
            
            # Define save path
            save_path = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/images/{snippet_number}.png"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Move downloaded file to target location
            shutil.move(download_path, save_path)
            logger.info(f"Image saved to {save_path}")
            
            page.keyboard.press("Escape")
            time.sleep(1)
            
            logger.info("✅ SUCCESS: Image generated and saved!")
            logger.info(f"📁 File saved to: {save_path}")
            print(f"SUCCESS: {save_path}")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error during image generation: {e}")
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 