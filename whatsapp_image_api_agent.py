from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os
import time
import shutil
import threading
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for session management
whatsapp_session_lock = threading.Lock()
whatsapp_context = None
whatsapp_page = None
session_initialized = False

def initialize_whatsapp_session():
    """Initialize WhatsApp Web session"""
    global whatsapp_context, whatsapp_page, session_initialized
    
    if session_initialized:
        return True
    
    try:
        whatsapp_url = "https://web.whatsapp.com/"
        chat_name = "ChatGPT"
        user_data_dir = os.path.abspath("whatsapp_session")
        downloads_dir = os.path.abspath(".whatsapp_downloads")
        
        logger.info("Initializing WhatsApp session...")
        
        # Create a new playwright instance for each initialization
        p = sync_playwright().start()
        whatsapp_context = p.chromium.launch_persistent_context(
            user_data_dir, 
            headless=False, 
            accept_downloads=True, 
            downloads_path=downloads_dir
        )
        whatsapp_page = whatsapp_context.new_page()
        whatsapp_page.goto(whatsapp_url)
        
        # Wait for WhatsApp to load
        chat_selector = f"span[title='{chat_name}']"
        whatsapp_page.wait_for_selector(chat_selector, timeout=120000)
        whatsapp_page.click(chat_selector)
        
        logger.info("WhatsApp session initialized successfully")
        session_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize WhatsApp session: {e}")
        return False

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
    global whatsapp_page, session_initialized
    
    if not session_initialized:
        logger.error("WhatsApp session not initialized")
        return False, "WhatsApp session not initialized"
    
    try:
        # Get message count before sending prompt
        message_count_before = get_message_count_before_prompts(whatsapp_page)
        logger.info(f"Messages before prompt: {message_count_before}")
        
        # Send the prompt
        if not send_prompt_with_retry(whatsapp_page, image_prompt):
            return False, "Failed to send prompt"
        
        # Wait for image generation
        img_src = wait_for_image_generation(whatsapp_page, message_count_before)
        if not img_src:
            return False, "Image generation failed or timed out"
        
        # Define save path
        save_path = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/images/{snippet_number}.png"
        
        # Download the image
        if download_image_by_src(whatsapp_page, img_src, save_path):
            return True, save_path
        else:
            return False, "Failed to download image"
            
    except Exception as e:
        logger.error(f"Error during image generation: {e}")
        return False, str(e)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "whatsapp_session": session_initialized,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """Generate image endpoint"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        required_fields = ['reel_number', 'snippet_number', 'image_prompt']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        reel_number = data['reel_number']
        snippet_number = data['snippet_number']
        image_prompt = data['image_prompt']
        
        # Validate data types
        if not isinstance(reel_number, (int, str)) or not isinstance(snippet_number, (int, str)):
            return jsonify({
                "success": False,
                "error": "reel_number and snippet_number must be numbers or strings"
            }), 400
        
        if not isinstance(image_prompt, str) or not image_prompt.strip():
            return jsonify({
                "success": False,
                "error": "image_prompt must be a non-empty string"
            }), 400
        
        logger.info(f"Received request: reel={reel_number}, snippet={snippet_number}, prompt={image_prompt[:50]}...")
        
        # Acquire lock for thread safety
        with whatsapp_session_lock:
            success, result = generate_single_image(reel_number, snippet_number, image_prompt)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Image generated successfully",
                "file_path": result,
                "reel_number": reel_number,
                "snippet_number": snippet_number
            })
        else:
            return jsonify({
                "success": False,
                "error": result
            }), 500
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/initialize-session', methods=['POST'])
def initialize_session():
    """Initialize WhatsApp session endpoint"""
    try:
        with whatsapp_session_lock:
            success = initialize_whatsapp_session()
        
        if success:
            return jsonify({
                "success": True,
                "message": "WhatsApp session initialized successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to initialize WhatsApp session"
            }), 500
            
    except Exception as e:
        logger.error(f"Session initialization error: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Initialize WhatsApp session on startup
    logger.info("Starting WhatsApp Image API Agent...")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5001, debug=False) 