#!/usr/bin/env python3
"""
Dreamina Upload API Server
Provides API endpoints for uploading image-audio pairs to Dreamina by reel number
"""

from flask import Flask, request, jsonify
import os
import logging
import threading
import queue
import time
import glob
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global queue for handling concurrent requests
request_queue = queue.Queue()
processing_lock = threading.Lock()
is_processing = False

class DreaminaUploadAPI:
    """
    API wrapper for Dreamina upload functionality
    """
    
    def __init__(self, user_data_dir="vpn_browser_session", headless=False):
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.headless = headless
        self.context = None
        self.page = None
        self.playwright = None
        
        # Create directories
        os.makedirs(self.user_data_dir, exist_ok=True)
        
    def launch_browser(self):
        """Launch browser with persistent session"""
        try:
            self.playwright = sync_playwright().start()
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                accept_downloads=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--allow-running-insecure-content"
                ]
            )
            
            self.page = self.context.new_page()
            logger.info("✅ Browser launched successfully")
            return True
                
        except Exception as e:
            logger.error(f"❌ Failed to launch browser: {e}")
            return False
    
    def navigate_to_dreamina(self):
        """Navigate directly to Dreamina AI Avatar page"""
        try:
            logger.info("🌐 Navigating to Dreamina AI Avatar page...")
            self.page.goto("https://dreamina.capcut.com/ai-tool/generate?type=digitalHuman")
            
            # Wait for page to load
            time.sleep(5)
            logger.info("✅ Dreamina AI Avatar page loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to Dreamina: {e}")
            return False
    
    def navigate_to_create_tab(self):
        """Ensure we're on the Create tab"""
        try:
            logger.info("📝 Ensuring we're on the Create tab...")
            
            create_tab_selectors = [
                'button:has-text("Create")',
                '[data-testid="create-tab"]',
                '.create-tab',
                'button[aria-label*="Create"]'
            ]
            
            create_tab = None
            for selector in create_tab_selectors:
                try:
                    create_tab = self.page.wait_for_selector(selector, timeout=5000)
                    if create_tab:
                        logger.info(f"✅ Found Create tab with selector: {selector}")
                        break
                except:
                    continue
            
            if create_tab:
                create_tab.click()
                time.sleep(2)
                logger.info("✅ Clicked Create tab")
                return True
            else:
                logger.warning("⚠️ Create tab not found, continuing anyway")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error navigating to Create tab: {e}")
            return False
    
    def navigate_to_ai_avatar(self):
        """Navigate to AI Avatar section"""
        try:
            logger.info("🤖 Navigating to AI Avatar section...")
            
            # Look for AI Avatar button
            avatar_selectors = [
                'button:has-text("AI Avatar")',
                '[data-testid="ai-avatar-button"]',
                '.ai-avatar-button',
                'button[aria-label*="AI Avatar"]',
                'div:has-text("AI Avatar")',
                'span:has-text("AI Avatar")'
            ]
            
            avatar_button = None
            for selector in avatar_selectors:
                try:
                    avatar_button = self.page.wait_for_selector(selector, timeout=3000)
                    if avatar_button:
                        logger.info(f"✅ Found AI Avatar button with selector: {selector}")
                        break
                except:
                    continue
            
            if avatar_button:
                avatar_button.click()
                time.sleep(3)
                logger.info("✅ Clicked AI Avatar button")
                return True
            else:
                logger.warning("⚠️ AI Avatar button not found, continuing anyway")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error navigating to AI Avatar: {e}")
            return False
    
    def upload_image(self, image_path):
        """Upload image file"""
        try:
            logger.info(f"📸 Uploading image: {image_path}")
            
            # Look for the Avatar upload button using the exact CSS classes
            avatar_button_selectors = [
                'div.reference-upload-vSJ7So:has(.label-TlzdqP:has-text("Avatar"))',
                'div.reference-upload-vSJ7So:has-text("Avatar")',
                'div[class*="reference-upload"]:has-text("Avatar")',
                'div:has(.label-TlzdqP:has-text("Avatar"))',
                'div:has-text("Avatar"):has(input[accept*="image"])'
            ]
            
            avatar_button = None
            for selector in avatar_button_selectors:
                try:
                    avatar_button = self.page.wait_for_selector(selector, timeout=5000)
                    if avatar_button:
                        logger.info(f"✅ Found Avatar button with selector: {selector}")
                        break
                except:
                    continue
            
            if not avatar_button:
                logger.error("❌ Could not find Avatar upload button")
                return False
            
            # Find the hidden file input within the Avatar button
            file_input = avatar_button.query_selector('input[type="file"][accept*="image"]')
            if not file_input:
                logger.error("❌ Could not find image file input")
                return False
            
            # Set the file directly to the input
            file_input.set_input_files(image_path)
            
            # Wait for upload to complete
            time.sleep(3)
            logger.info("✅ Image upload completed")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error uploading image: {e}")
            return False
    
    def upload_audio(self, audio_path):
        """Upload audio file"""
        try:
            logger.info(f"🎵 Uploading audio: {audio_path}")
            
            # Look for the Speech upload button using the exact CSS classes
            audio_button_selectors = [
                'div.reference-upload-vSJ7So:has(.label-TlzdqP:has-text("Speech"))',
                'div.reference-upload-vSJ7So:has-text("Speech")',
                'div[class*="reference-upload"]:has-text("Speech")',
                'div:has(.label-TlzdqP:has-text("Speech"))',
                'div:has-text("Speech"):has(input[accept*="audio"])'
            ]
            
            audio_button = None
            for selector in audio_button_selectors:
                try:
                    audio_button = self.page.wait_for_selector(selector, timeout=5000)
                    if audio_button:
                        logger.info(f"✅ Found Speech button with selector: {selector}")
                        break
                except:
                    continue
            
            if not audio_button:
                logger.error("❌ Could not find Speech upload button")
                return False
            
            # Find the hidden file input within the Speech button
            file_input = audio_button.query_selector('input[type="file"][accept*="audio"]')
            if not file_input:
                logger.error("❌ Could not find audio file input")
                return False
            
            # Set the file directly to the input
            file_input.set_input_files(audio_path)
            
            # Wait for upload to complete
            time.sleep(3)
            logger.info("✅ Audio upload completed")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error uploading audio: {e}")
            return False
    
    def submit_upload(self):
        """Submit the upload"""
        try:
            logger.info("🚀 Submitting upload...")
            
            # Look for the submit button using the exact CSS classes
            upload_selectors = [
                'button.lv-btn.lv-btn-primary.lv-btn-size-default.lv-btn-shape-circle.lv-btn-icon-only.submit-button-bPnDkw',
                'button.submit-button-bPnDkw',
                'button.lv-btn-primary.lv-btn-shape-circle.lv-btn-icon-only',
                'button:has(svg[data-follow-fill="currentColor"])',
                'button[type="button"]:has(svg)',
                'button.lv-btn:has(svg)',
                'button:has-text("Submit")',
                'button:has-text("Generate")',
                'button:has-text("Create")',
                'button:has-text("Upload")',
                'button:has-text("Start")'
            ]
            
            upload_button = None
            for selector in upload_selectors:
                try:
                    upload_button = self.page.wait_for_selector(selector, timeout=5000)
                    if upload_button:
                        logger.info(f"✅ Found upload button with selector: {selector}")
                        break
                except:
                    continue
            
            if not upload_button:
                logger.error("❌ Could not find upload button")
                return False
            
            # Check if button is disabled
            is_disabled = upload_button.get_attribute('disabled')
            if is_disabled:
                logger.warning("⚠️ Upload button is disabled, waiting for it to become enabled...")
                # Wait for button to become enabled
                try:
                    self.page.wait_for_selector(f'{selector}:not([disabled])', timeout=30000)
                    upload_button = self.page.query_selector(selector)
                    if not upload_button:
                        logger.error("❌ Upload button still not found after waiting")
                        return False
                except:
                    logger.error("❌ Upload button did not become enabled within timeout")
                    return False
            
            # Click the upload button
            upload_button.click()
            
            # Wait for upload to process
            logger.info("⏳ Upload submitted, waiting for processing...")
            time.sleep(5)
            
            logger.info("✅ Upload submitted successfully")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error submitting upload: {e}")
            return False
    
    def check_for_errors(self):
        """Check if there are any error messages"""
        try:
            error_selectors = [
                'div.error-tips-Smo0rk',
                '.error-tips-text-xJxpf1',
                '.error-tips-Smo0rk .error-tips-text-xJxpf1',
                '.error-message',
                '.alert-error',
                '[data-testid="error"]',
                'div[role="alert"]',
                '.notification-error'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.page.query_selector(selector)
                    if error_element:
                        error_text = error_element.inner_text()
                        if error_text and error_text.strip():
                            logger.error(f"❌ Error detected: {error_text}")
                            return True, error_text.strip()
                except:
                    continue
            
            return False, None
            
        except Exception as e:
            logger.error(f"❌ Error checking for errors: {e}")
            return False, None
    
    def wait_for_generation(self, timeout=300):
        """Wait for video generation to complete or error to occur"""
        try:
            logger.info(f"⏳ Waiting for video generation (timeout: {timeout}s)...")
            
            start_time = time.time()
            error_check_start = time.time()
            
            while time.time() - start_time < timeout:
                # Check for completion indicators
                completion_selectors = [
                    '.generation-complete',
                    '[data-testid="generation-complete"]',
                    '.success-message',
                    'button:has-text("Download")'
                ]
                
                for selector in completion_selectors:
                    try:
                        element = self.page.query_selector(selector)
                        if element:
                            logger.info("✅ Video generation completed")
                            return True, None
                    except:
                        continue
                
                # Check for errors
                has_error, error_message = self.check_for_errors()
                if has_error:
                    logger.error(f"❌ Error during generation: {error_message}")
                    return False, error_message
                
                # After 60 seconds of no errors, assume generation is in progress
                if time.time() - error_check_start > 60:
                    logger.info("✅ No errors for 60 seconds - video generation in progress")
                    return True, "generation_in_progress"
                
                time.sleep(5)
            
            logger.warning("⚠️ Generation timeout reached")
            return False, "Generation timeout reached"
            
        except Exception as e:
            logger.error(f"❌ Error waiting for generation: {e}")
            return False, str(e)
    
    def get_file_pairs(self, reel_number):
        """Get image-audio file pairs for a reel"""
        try:
            base_path = f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}"
            images_dir = f"{base_path}/Images"
            audio_dir = f"{base_path}/Audio"
            
            # Check if directories exist
            if not os.path.exists(images_dir):
                logger.error(f"❌ Images directory not found: {images_dir}")
                return []
            
            if not os.path.exists(audio_dir):
                logger.error(f"❌ Audio directory not found: {audio_dir}")
                return []
            
            # Get all image files
            image_files = glob.glob(f"{images_dir}/*")
            image_files = [f for f in image_files if os.path.isfile(f)]
            image_files.sort()
            
            # Get all audio files
            audio_files = glob.glob(f"{audio_dir}/*")
            audio_files = [f for f in audio_files if os.path.isfile(f)]
            audio_files.sort()
            
            # Create pairs (assuming files are numbered 1, 2, 3, etc.)
            pairs = []
            for i in range(1, max(len(image_files), len(audio_files)) + 1):
                # Look for files with number i
                matching_images = [f for f in image_files if str(i) in os.path.basename(f)]
                matching_audios = [f for f in audio_files if str(i) in os.path.basename(f)]
                
                if matching_images and matching_audios:
                    pairs.append({
                        'number': i,
                        'image': matching_images[0],
                        'audio': matching_audios[0]
                    })
            
            logger.info(f"📁 Found {len(pairs)} file pairs for reel {reel_number}")
            return pairs
            
        except Exception as e:
            logger.error(f"❌ Error getting file pairs: {e}")
            return []
    
    def upload_file_pair(self, image_path, audio_path, pair_number):
        """Upload a single image-audio pair"""
        try:
            logger.info(f"🔄 Uploading pair {pair_number}: {os.path.basename(image_path)} + {os.path.basename(audio_path)}")
            
            # Upload image
            if not self.upload_image(image_path):
                logger.error(f"❌ Failed to upload image for pair {pair_number}")
                return False, "Failed to upload image"
            
            # Upload audio
            if not self.upload_audio(audio_path):
                logger.error(f"❌ Failed to upload audio for pair {pair_number}")
                return False, "Failed to upload audio"
            
            # Submit upload
            if not self.submit_upload():
                logger.error(f"❌ Failed to submit upload for pair {pair_number}")
                return False, "Failed to submit upload"
            
            # Wait for generation
            success, status_message = self.wait_for_generation()
            if not success:
                logger.error(f"❌ Generation failed for pair {pair_number}: {status_message}")
                return False, status_message
            
            # If generation is in progress, remove files and continue
            if status_message == "generation_in_progress":
                logger.info(f"✅ Pair {pair_number} generation started successfully")
                if not self.remove_uploaded_files():
                    logger.warning(f"⚠️ Failed to remove files for pair {pair_number}, but continuing...")
                return True, "generation_started"
            
            logger.info(f"✅ Successfully uploaded pair {pair_number}")
            return True, None
            
        except Exception as e:
            logger.error(f"❌ Error uploading pair {pair_number}: {e}")
            return False, str(e)
    
    def upload_reel_files(self, reel_number):
        """Upload all file pairs for a reel"""
        try:
            logger.info(f"🎬 Starting upload for reel {reel_number}")
            
            # Launch browser
            if not self.launch_browser():
                return {"success": False, "error": "Failed to launch browser"}
            
            # Navigate to Dreamina
            if not self.navigate_to_dreamina():
                return {"success": False, "error": "Failed to navigate to Dreamina"}
            
            # Navigate to Create tab
            if not self.navigate_to_create_tab():
                return {"success": False, "error": "Failed to navigate to Create tab"}
            
            # Navigate to AI Avatar
            if not self.navigate_to_ai_avatar():
                return {"success": False, "error": "Failed to navigate to AI Avatar"}
            
            # Get file pairs
            file_pairs = self.get_file_pairs(reel_number)
            if not file_pairs:
                return {"success": False, "error": "No file pairs found"}
            
            # Upload each pair
            results = []
            for pair in file_pairs:
                success, status_message = self.upload_file_pair(
                    pair['image'], 
                    pair['audio'], 
                    pair['number']
                )
                
                results.append({
                    'pair_number': pair['number'],
                    'image': os.path.basename(pair['image']),
                    'audio': os.path.basename(pair['audio']),
                    'success': success,
                    'status': status_message
                })
                
                # Stop only if there's a real error (not generation_in_progress)
                if not success and status_message != "generation_started":
                    logger.warning(f"⚠️ Stopping upload due to failure in pair {pair['number']}")
                    break
                
                # If generation started successfully, continue to next pair
                if success and status_message == "generation_started":
                    logger.info(f"✅ Continuing to next pair after successful generation start for pair {pair['number']}")
                    continue
            
            # Close browser
            self.close()
            
            return {
                "success": True,
                "reel_number": reel_number,
                "total_pairs": len(file_pairs),
                "uploaded_pairs": len([r for r in results if r['success']]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Error uploading reel {reel_number}: {e}")
            if self.context:
                self.close()
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close browser"""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("✅ Browser closed")
        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")

    def remove_uploaded_files(self):
        """Click remove buttons to clear uploaded image and audio files"""
        try:
            logger.info("🗑️ Removing uploaded files...")
            
            # Look for remove buttons
            remove_button_selectors = [
                'div.remove-button-container-yw3VKU .remove-button-dh1E0f',
                '.remove-button-dh1E0f',
                'div.remove-button-container-yw3VKU',
                'div:has(svg[data-follow-fill="currentColor"]):has(path[d*="19.579 6.119"])'
            ]
            
            remove_buttons = []
            for selector in remove_button_selectors:
                try:
                    buttons = self.page.query_selector_all(selector)
                    if buttons:
                        remove_buttons.extend(buttons)
                        logger.info(f"✅ Found {len(buttons)} remove buttons with selector: {selector}")
                except:
                    continue
            
            if not remove_buttons:
                logger.warning("⚠️ No remove buttons found")
                return False
            
            # Click all remove buttons
            for i, button in enumerate(remove_buttons):
                try:
                    button.click()
                    logger.info(f"✅ Clicked remove button {i+1}")
                    time.sleep(1)  # Small delay between clicks
                except Exception as e:
                    logger.error(f"❌ Failed to click remove button {i+1}: {e}")
            
            logger.info("✅ Successfully removed uploaded files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing uploaded files: {e}")
            return False

def process_queue():
    """Background thread to process requests one at a time"""
    global is_processing
    
    while True:
        try:
            # Get next request from queue
            request_data = request_queue.get(timeout=1)
            if request_data is None:  # Shutdown signal
                break
                
            with processing_lock:
                is_processing = True
                
            try:
                # Process the request
                reel_number = request_data['reel_number']
                logger.info(f"Processing Dreamina upload request for reel: {reel_number}")
                
                # Create upload agent and process
                agent = DreaminaUploadAPI(headless=False)
                result = agent.upload_reel_files(reel_number)
                
                # Store result for the waiting thread
                request_data['result'] = result
                request_data['completed'] = True
                
            except Exception as e:
                logger.error(f"Error processing Dreamina upload request: {e}")
                request_data['error'] = str(e)
                request_data['completed'] = True
                
            finally:
                with processing_lock:
                    is_processing = False
                    
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error in queue processing: {e}")

# Start the background processing thread
queue_thread = threading.Thread(target=process_queue, daemon=True)
queue_thread.start()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    queue_size = request_queue.qsize()
    return jsonify({
        "status": "healthy",
        "message": "Dreamina Upload API is running",
        "timestamp": "2025-08-05T17:50:00.000000",
        "queue_size": queue_size,
        "is_processing": is_processing
    })

@app.route('/upload-reel-to-dreamina', methods=['POST'])
def upload_reel_to_dreamina():
    """Upload image-audio pairs to Dreamina for a reel endpoint"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        if 'reel_number' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: reel_number"
            }), 400
        
        reel_number = data['reel_number']
        
        # Check if already processing
        if is_processing:
            return jsonify({
                "success": False,
                "error": "Another upload is currently in progress. Please wait.",
                "queue_position": request_queue.qsize() + 1
            }), 429
        
        # Add request to queue
        request_data = {
            'reel_number': reel_number,
            'completed': False,
            'result': None,
            'error': None
        }
        
        request_queue.put(request_data)
        logger.info(f"Added reel {reel_number} to upload queue")
        
        # Wait for completion
        while not request_data['completed']:
            time.sleep(1)
        
        # Return result
        if request_data['error']:
            return jsonify({
                "success": False,
                "error": request_data['error']
            }), 500
        
        return jsonify(request_data['result'])
        
    except Exception as e:
        logger.error(f"Error in upload_reel_to_dreamina endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/upload-status', methods=['GET'])
def upload_status():
    """Get current upload status"""
    return jsonify({
        "is_processing": is_processing,
        "queue_size": request_queue.qsize(),
        "message": "Dreamina Upload API Status"
    })

if __name__ == '__main__':
    logger.info("🎬 Starting Dreamina Upload API Server...")
    logger.info("📋 Features:")
    logger.info("   ✅ Queue system for concurrent requests")
    logger.info("   ✅ Sequential file pair upload")
    logger.info("   ✅ Error handling and recovery")
    logger.info("   ✅ Progress tracking")
    logger.info("   ✅ Browser automation")
    logger.info("==================================================")
    
    app.run(host='0.0.0.0', port=5678, debug=False) 