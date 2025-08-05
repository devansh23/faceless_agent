#!/usr/bin/env python3
"""
Simple script to generate a single image using WhatsApp/ChatGPT
Usage: python3 generate_single_image.py <reel_number> <snippet_number> <image_prompt>
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

def initialize_whatsapp_session():
    """Initialize WhatsApp Web session"""
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
            return page, context
            
    except Exception as e:
        logger.error(f"Failed to initialize WhatsApp session: {e}")
        return None, None

def send_prompt_with_retry(page, prompt, max_retries=3):
    """Send prompt to ChatGPT with retry logic"""
    for attempt in range(max_retries):
        try:
            input_box_selector = 'div[contenteditable="true"][data-tab="10"]'
            page.wait_for_selector(input_box_selector, timeout=10000)
            page.fill(input_box_selector, prompt)
            page.keyboard.press("Enter")
            logger.info(f"Successfully sent prompt: {prompt[:40]}...")
            return True
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error(f"Failed to send prompt after {max_retries} attempts")
                return False

def get_message_count_before_prompts(page):
    """Get the number of messages before sending prompts"""
    messages = page.query_selector_all(".message-in")
    return len(messages)

def wait_for_image_generation(page, message_count_before_prompts, timeout_minutes=10):
    """Wait for image to be generated and return the image src"""
    logger.info(f"Waiting for image generation (timeout: {timeout_minutes} minutes)...")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while time.time() - start_time < timeout_seconds:
        # Get all messages
        all_messages = page.query_selector_all(".message-in")
        new_messages = all_messages[message_count_before_prompts:]
        
        # Look for new images
        for i, bubble in enumerate(new_messages):
            img_elem = bubble.query_selector("img[src^='blob:']")
            if img_elem:
                img_src = img_elem.get_attribute('src')
                if img_src:
                    logger.info(f"Image found in message {message_count_before_prompts + i + 1}")
                    return img_src
        
        # Check for error messages
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
                    logger.error(f"Error detected in message: {indicator}")
                    return None
        
        time.sleep(30)  # Check every 30 seconds
        elapsed_minutes = int((time.time() - start_time) / 60)
        logger.info(f"Still waiting... ({elapsed_minutes}/{timeout_minutes} minutes elapsed)")
    
    logger.error(f"Timeout reached after {timeout_minutes} minutes")
    return None

def download_image_by_src(page, img_src, save_path):
    """Download image by src and save to specified path"""
    try:
        img_elem = page.query_selector(f"img[src='{img_src}']")
        if not img_elem:
            logger.error(f"Image not found with src {img_src}")
            return False
        
        img_elem.click()
        download_btn_selector = 'span[data-icon="download-refreshed"]'
        page.wait_for_selector(download_btn_selector, timeout=20000)
        
        with page.expect_download() as download_info:
            page.click(download_btn_selector)
        
        download = download_info.value
        download_path = download.path()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Move downloaded file to target location
        shutil.move(download_path, save_path)
        logger.info(f"Image saved to {save_path}")
        
        page.keyboard.press("Escape")
        time.sleep(1)
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

def generate_single_image(reel_number, snippet_number, image_prompt):
    """Generate a single image using WhatsApp"""
    logger.info(f"Starting image generation for reel={reel_number}, snippet={snippet_number}")
    logger.info(f"Prompt: {image_prompt}")
    
    # Initialize WhatsApp session
    page, context = initialize_whatsapp_session()
    if not page:
        logger.error("Failed to initialize WhatsApp session")
        return False, "Failed to initialize WhatsApp session"
    
    try:
        # Get message count before sending prompt
        message_count_before = get_message_count_before_prompts(page)
        logger.info(f"Messages before prompt: {message_count_before}")
        
        # Send the prompt
        if not send_prompt_with_retry(page, image_prompt):
            return False, "Failed to send prompt"
        
        # Wait for image generation
        img_src = wait_for_image_generation(page, message_count_before)
        if not img_src:
            return False, "Image generation failed or timed out"
        
        # Define save path
        save_path = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/images/{snippet_number}.png"
        
        # Download the image
        if download_image_by_src(page, img_src, save_path):
            logger.info(f"✅ Image generated successfully: {save_path}")
            return True, save_path
        else:
            return False, "Failed to download image"
            
    except Exception as e:
        logger.error(f"Error during image generation: {e}")
        return False, str(e)
    # Context will be closed automatically when the with statement ends

def main():
    """Main function"""
    if len(sys.argv) != 4:
        print("Usage: python3 generate_single_image.py <reel_number> <snippet_number> <image_prompt>")
        print("Example: python3 generate_single_image.py test 001 'A simple red circle on white background'")
        sys.exit(1)
    
    reel_number = sys.argv[1]
    snippet_number = sys.argv[2]
    image_prompt = sys.argv[3]
    
    logger.info("=" * 60)
    logger.info("🎨 WhatsApp Image Generation Script")
    logger.info("=" * 60)
    
    # Generate the image
    success, result = generate_single_image(reel_number, snippet_number, image_prompt)
    
    if success:
        logger.info("✅ SUCCESS: Image generated and saved!")
        logger.info(f"📁 File saved to: {result}")
        print(f"SUCCESS: {result}")
        sys.exit(0)
    else:
        logger.error("❌ FAILED: Image generation failed!")
        logger.error(f"Error: {result}")
        print(f"ERROR: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main() 