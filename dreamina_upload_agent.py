#!/usr/bin/env python3
"""
Dreamina Upload Automation Agent
Automates uploading image-audio pairs to Dreamina's AI Avatar feature
"""

import os
import time
import glob
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

class DreaminaUploadAgent:
    """
    Automation agent for uploading image-audio pairs to Dreamina
    """
    
    def __init__(self, user_data_dir="vpn_browser_session", headless=False):
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.headless = headless
        self.context = None
        self.page = None
        self.playwright = None
        
        # File paths
        self.images_dir = os.path.abspath("images")
        self.audio_dir = os.path.abspath("audio")
        
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
            print("✅ Browser launched successfully")
            return True
                
        except Exception as e:
            print(f"❌ Failed to launch browser: {e}")
            return False
    
    def navigate_to_dreamina(self):
        """Navigate directly to Dreamina AI Avatar page"""
        try:
            print("🌐 Navigating directly to Dreamina AI Avatar page...")
            self.page.goto("https://dreamina.capcut.com/ai-tool/generate?type=digitalHuman")
            
            # Wait a bit for the page to load
            time.sleep(5)
            print("✅ Dreamina AI Avatar page loaded successfully")
            
            # Print current URL and title for debugging
            print(f"📄 Current URL: {self.page.url}")
            print(f"📄 Page title: {self.page.title()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to navigate to Dreamina AI Avatar page: {e}")
            return False
    
    def navigate_to_create_tab(self):
        """Ensure we're on the Create tab"""
        try:
            print("📝 Ensuring we're on the Create tab...")
            
            # Look for the Create tab in the left sidebar
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
                        print(f"✅ Found Create tab with selector: {selector}")
                        break
                except:
                    continue
            
            if create_tab:
                # Always click the Create tab, regardless of current state
                print("🔄 Clicking Create tab...")
                create_tab.click()
                time.sleep(2)
                print("✅ Create tab clicked")
            else:
                print("⚠️  Could not find Create tab, assuming we're already on it")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to navigate to Create tab: {e}")
            return False
    
    def navigate_to_ai_avatar(self):
        """Navigate to the AI Avatar section"""
        try:
            print("🎭 Navigating to AI Avatar section...")
            
            # First ensure we're on the Create tab
            if not self.navigate_to_create_tab():
                return False
            
            # Look for the AI Avatar button in the top banner
            # Based on the UI description, it's in the top blue banner with other AI options
            ai_avatar_selectors = [
                'div:has-text("AI Avatar"):not(:has-text("AI Image"))',
                'button:has-text("AI Avatar")',
                '[data-testid="ai-avatar-button"]',
                '.ai-avatar-button',
                'button[aria-label*="AI Avatar"]',
                'div:has-text("AI Avatar")',
                'span:has-text("AI Avatar")',
                'button:has-text("Avatar")',
                'div[role="button"]:has-text("AI Avatar")',
                'div[role="tab"]:has-text("AI Avatar")',
                'div[role="option"]:has-text("AI Avatar")'
            ]
            
            ai_avatar_button = None
            for selector in ai_avatar_selectors:
                try:
                    ai_avatar_button = self.page.wait_for_selector(selector, timeout=5000)
                    if ai_avatar_button:
                        print(f"✅ Found AI Avatar button with selector: {selector}")
                        break
                except:
                    continue
            
            if not ai_avatar_button:
                print("⚠️  Could not find AI Avatar button automatically")
                print("   Please manually click on 'AI Avatar' in the top banner")
                input("Press Enter when AI Avatar mode is selected...")
                return True
            
            # Try different click methods to bypass element interception
            print("🔄 Attempting to click AI Avatar button...")
            
            # Method 1: Try JavaScript click
            try:
                self.page.evaluate("arguments[0].click();", ai_avatar_button)
                print("✅ Clicked using JavaScript")
            except Exception as e:
                print(f"⚠️  JavaScript click failed: {e}")
                
                # Method 2: Try force click
                try:
                    ai_avatar_button.click(force=True)
                    print("✅ Clicked using force click")
                except Exception as e2:
                    print(f"⚠️  Force click failed: {e2}")
                    
                    # Method 3: Try clicking at specific coordinates
                    try:
                        # Get element position and click at center
                        box = ai_avatar_button.bounding_box()
                        if box:
                            x = box['x'] + box['width'] / 2
                            y = box['y'] + box['height'] / 2
                            self.page.mouse.click(x, y)
                            print("✅ Clicked using mouse coordinates")
                        else:
                            raise Exception("Could not get element position")
                    except Exception as e3:
                        print(f"⚠️  Coordinate click failed: {e3}")
                        print("   Please manually click on 'AI Avatar' in the top banner")
                        input("Press Enter when AI Avatar mode is selected...")
                        return True
            
            time.sleep(3)  # Wait for the interface to switch to AI Avatar mode
            
            # Verify we're now in AI Avatar mode by checking if we can find the Avatar/Speech cards
            print("🔍 Verifying AI Avatar mode...")
            avatar_card_selectors = [
                'div:has-text("Avatar")',
                'button:has-text("Avatar")',
                'div[role="button"]:has-text("Avatar")'
            ]
            
            avatar_found = False
            for selector in avatar_card_selectors:
                try:
                    if self.page.wait_for_selector(selector, timeout=3000):
                        print(f"✅ Found Avatar card with selector: {selector}")
                        avatar_found = True
                        break
                except:
                    continue
            
            if avatar_found:
                print("✅ AI Avatar mode selected successfully")
                return True
            else:
                print("⚠️  AI Avatar mode may not have been selected properly")
                print("   Please manually click on 'AI Avatar' in the top banner")
                input("Press Enter when AI Avatar mode is selected...")
                return True
            
        except Exception as e:
            print(f"❌ Failed to navigate to AI Avatar: {e}")
            return False
    
    def upload_image(self, image_path):
        """Upload image file to Dreamina"""
        try:
            print(f"🖼️  Uploading image: {os.path.basename(image_path)}")
            
            # Look for the Avatar upload button - based on the interface, it's a card with "Avatar" text
            avatar_button_selectors = [
                'div:has-text("Avatar")',
                'button:has-text("Avatar")',
                '[data-testid="avatar-upload-button"]',
                '.avatar-upload-button',
                'button[aria-label*="Avatar"]',
                'div[role="button"]:has-text("Avatar")',
                'div:has-text("Avatar"):has(> svg)',
                'div:has-text("Avatar"):has(> .plus-icon)'
            ]
            
            avatar_button = None
            for selector in avatar_button_selectors:
                try:
                    avatar_button = self.page.wait_for_selector(selector, timeout=5000)
                    if avatar_button:
                        print(f"✅ Found Avatar button with selector: {selector}")
                        break
                except:
                    continue
            
            if not avatar_button:
                print("❌ Could not find Avatar upload button")
                return False
            
            # Click the Avatar button to trigger file upload
            avatar_button.click()
            time.sleep(1)
            
            # Handle file upload
            with self.page.expect_file_chooser() as fc_info:
                avatar_button.click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(image_path)
            
            # Wait for upload to complete
            time.sleep(3)
            print("✅ Image upload completed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload image: {e}")
            return False
    
    def upload_audio(self, audio_path):
        """Upload audio file to Dreamina"""
        try:
            print(f"🎵 Uploading audio: {os.path.basename(audio_path)}")
            
            # Look for the Speech/Audio upload button - based on the interface, it's a card with "Speech" text
            audio_button_selectors = [
                'div:has-text("Speech")',
                'button:has-text("Speech")',
                '[data-testid="speech-upload-button"]',
                '.speech-upload-button',
                'button[aria-label*="Speech"]',
                'div[role="button"]:has-text("Speech")',
                'div:has-text("Speech"):has(> svg)',
                'div:has-text("Speech"):has(> .waveform-icon)'
            ]
            
            audio_button = None
            for selector in audio_button_selectors:
                try:
                    audio_button = self.page.wait_for_selector(selector, timeout=5000)
                    if audio_button:
                        print(f"✅ Found Speech button with selector: {selector}")
                        break
                except:
                    continue
            
            if not audio_button:
                print("❌ Could not find Speech upload button")
                return False
            
            # Click the Speech button to trigger file upload
            audio_button.click()
            time.sleep(1)
            
            # Handle file upload
            with self.page.expect_file_chooser() as fc_info:
                audio_button.click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(audio_path)
            
            # Wait for upload to complete
            time.sleep(3)
            print("✅ Audio upload completed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload audio: {e}")
            return False
    
    def submit_upload(self):
        """Submit the upload by clicking the upload CTA"""
        try:
            print("⬆️  Submitting upload...")
            
            # Look for the upload CTA button - based on the interface, it's a circular button with upward arrow
            upload_selectors = [
                'button:has(svg[data-icon="upload"])',
                'button:has(svg[data-icon="arrow-up"])',
                'button:has(svg[data-icon="chevron-up"])',
                'button[aria-label*="Upload"]',
                'button[aria-label*="Submit"]',
                'button:has-text("Upload")',
                'button:has-text("Submit")',
                'button:has-text("Create")',
                'button:has-text("Generate")',
                'button:has-text("Start")',
                'div[role="button"]:has(svg[data-icon="upload"])',
                'div[role="button"]:has(svg[data-icon="arrow-up"])',
                'button:has(> svg[data-icon*="up"])',
                'button:has(> svg[data-icon*="upload"])'
            ]
            
            upload_button = None
            for selector in upload_selectors:
                try:
                    upload_button = self.page.wait_for_selector(selector, timeout=5000)
                    if upload_button:
                        print(f"✅ Found upload button with selector: {selector}")
                        break
                except:
                    continue
            
            if not upload_button:
                print("❌ Could not find upload button")
                return False
            
            # Click the upload button
            upload_button.click()
            
            # Wait for upload to process
            print("⏳ Upload submitted, waiting for processing...")
            time.sleep(5)
            
            print("✅ Upload submitted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to submit upload: {e}")
            return False
    
    def get_available_files(self):
        """Get list of available image and audio files"""
        try:
            # Get image files
            image_files = []
            for reel_dir in os.listdir(self.images_dir):
                reel_path = os.path.join(self.images_dir, reel_dir)
                if os.path.isdir(reel_path):
                    for img_file in os.listdir(reel_path):
                        if img_file.endswith(('.png', '.jpg', '.jpeg')):
                            image_files.append({
                                'reel': reel_dir,
                                'file': img_file,
                                'path': os.path.join(reel_path, img_file)
                            })
            
            # Get audio files
            audio_files = []
            for reel_dir in os.listdir(self.audio_dir):
                reel_path = os.path.join(self.audio_dir, reel_dir)
                if os.path.isdir(reel_path):
                    for audio_file in os.listdir(reel_path):
                        if audio_file.endswith(('.mp3', '.wav', '.m4a')):
                            audio_files.append({
                                'reel': reel_dir,
                                'file': audio_file,
                                'path': os.path.join(reel_path, audio_file)
                            })
            
            return image_files, audio_files
            
        except Exception as e:
            print(f"❌ Error getting available files: {e}")
            return [], []
    
    def upload_file_pair(self, image_path, audio_path):
        """Upload a single image-audio pair"""
        try:
            print(f"\n🎬 Uploading file pair:")
            print(f"   Image: {os.path.basename(image_path)}")
            print(f"   Audio: {os.path.basename(audio_path)}")
            
            # Upload image
            if not self.upload_image(image_path):
                return False
            
            # Upload audio
            if not self.upload_audio(audio_path):
                return False
            
            # Submit upload
            if not self.submit_upload():
                return False
            
            print("✅ File pair uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload file pair: {e}")
            return False
    
    def batch_upload(self, max_files=None):
        """Upload multiple image-audio pairs"""
        try:
            print("🚀 Starting batch upload to Dreamina...")
            
            # Get available files
            image_files, audio_files = self.get_available_files()
            
            if not image_files or not audio_files:
                print("❌ No image or audio files found")
                return False
            
            print(f"📁 Found {len(image_files)} images and {len(audio_files)} audio files")
            
            # Match files by reel number and line number
            successful_uploads = 0
            failed_uploads = 0
            
            # Group files by reel
            image_by_reel = {}
            for img in image_files:
                if img['reel'] not in image_by_reel:
                    image_by_reel[img['reel']] = []
                image_by_reel[img['reel']].append(img)
            
            audio_by_reel = {}
            for audio in audio_files:
                if audio['reel'] not in audio_by_reel:
                    audio_by_reel[audio['reel']] = []
                audio_by_reel[audio['reel']].append(audio)
            
            # Process each reel
            for reel in sorted(image_by_reel.keys()):
                if reel in audio_by_reel:
                    reel_images = sorted(image_by_reel[reel], key=lambda x: x['file'])
                    reel_audios = sorted(audio_by_reel[reel], key=lambda x: x['file'])
                    
                    # Match files by line number
                    for i, (img, audio) in enumerate(zip(reel_images, reel_audios)):
                        if max_files and successful_uploads >= max_files:
                            break
                        
                        print(f"\n📦 Processing reel {reel}, pair {i+1}/{len(reel_images)}")
                        
                        if self.upload_file_pair(img['path'], audio['path']):
                            successful_uploads += 1
                        else:
                            failed_uploads += 1
                        
                        # Wait between uploads
                        time.sleep(2)
            
            print(f"\n🎉 Batch upload completed!")
            print(f"   ✅ Successful: {successful_uploads}")
            print(f"   ❌ Failed: {failed_uploads}")
            
            return successful_uploads > 0
            
        except Exception as e:
            print(f"❌ Batch upload failed: {e}")
            return False
    
    def close(self):
        """Close the browser session"""
        if self.context:
            try:
                self.context.close()
                print("✅ Browser session closed")
            except Exception as e:
                print(f"⚠️  Browser close error (ignored): {e}")
        
        if self.playwright:
            try:
                self.playwright.stop()
                print("✅ Playwright stopped")
            except Exception as e:
                print(f"⚠️  Playwright stop error (ignored): {e}")

    def test_avatar_button_click(self):
        """Test clicking the Avatar button without file upload"""
        try:
            print("🖼️  Testing Avatar button click...")
            
            # Look for the Avatar upload button
            avatar_button_selectors = [
                'div:has-text("Avatar")',
                'button:has-text("Avatar")',
                '[data-testid="avatar-upload-button"]',
                '.avatar-upload-button',
                'button[aria-label*="Avatar"]',
                'div[role="button"]:has-text("Avatar")',
                'div:has-text("Avatar"):has(> svg)',
                'div:has-text("Avatar"):has(> .plus-icon)'
            ]
            
            avatar_button = None
            for selector in avatar_button_selectors:
                try:
                    avatar_button = self.page.wait_for_selector(selector, timeout=5000)
                    if avatar_button:
                        print(f"✅ Found Avatar button with selector: {selector}")
                        break
                except:
                    continue
            
            if not avatar_button:
                print("❌ Could not find Avatar button")
                return False
            
            # Just click the button without expecting file chooser
            print("🔄 Clicking Avatar button...")
            avatar_button.click()
            time.sleep(2)
            
            print("✅ Avatar button clicked successfully!")
            print("🔍 Check if the file chooser dialog opened or if there's any visual feedback")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to click Avatar button: {e}")
            return False

    def debug_avatar_button(self):
        """Debug the Avatar button to understand why it's not clickable"""
        try:
            print("🔍 Debugging Avatar button...")
            
            # Look for the Avatar upload button with more detailed logging
            avatar_button_selectors = [
                'div:has-text("Avatar")',
                'button:has-text("Avatar")',
                '[data-testid="avatar-upload-button"]',
                '.avatar-upload-button',
                'button[aria-label*="Avatar"]',
                'div[role="button"]:has-text("Avatar")',
                'div:has-text("Avatar"):has(> svg)',
                'div:has-text("Avatar"):has(> .plus-icon)'
            ]
            
            avatar_button = None
            used_selector = None
            
            for selector in avatar_button_selectors:
                try:
                    print(f"🔍 Trying selector: {selector}")
                    avatar_button = self.page.wait_for_selector(selector, timeout=3000)
                    if avatar_button:
                        used_selector = selector
                        print(f"✅ Found Avatar button with selector: {selector}")
                        break
                except Exception as e:
                    print(f"❌ Selector failed: {selector} - {e}")
                    continue
            
            if not avatar_button:
                print("❌ Could not find Avatar button with any selector")
                print("🔍 Let's look for all elements containing 'Avatar' text...")
                
                # Try to find any element with "Avatar" text
                all_avatar_elements = self.page.query_selector_all('*:has-text("Avatar")')
                print(f"📋 Found {len(all_avatar_elements)} elements containing 'Avatar' text")
                
                for i, elem in enumerate(all_avatar_elements):
                    try:
                        tag_name = elem.evaluate('el => el.tagName')
                        class_name = elem.evaluate('el => el.className')
                        text_content = elem.evaluate('el => el.textContent')
                        print(f"   Element {i+1}: {tag_name}, class='{class_name}', text='{text_content}'")
                    except:
                        print(f"   Element {i+1}: Could not get details")
                
                return False
            
            # Get detailed information about the found button
            print(f"\n📋 Avatar button details:")
            try:
                tag_name = avatar_button.evaluate('el => el.tagName')
                class_name = avatar_button.evaluate('el => el.className')
                text_content = avatar_button.evaluate('el => el.textContent')
                is_visible = avatar_button.is_visible()
                is_enabled = avatar_button.is_enabled()
                
                print(f"   Tag: {tag_name}")
                print(f"   Class: {class_name}")
                print(f"   Text: {text_content}")
                print(f"   Visible: {is_visible}")
                print(f"   Enabled: {is_enabled}")
                
                if not is_visible:
                    print("⚠️  Button is not visible!")
                    return False
                
                if not is_enabled:
                    print("⚠️  Button is not enabled!")
                    return False
                
            except Exception as e:
                print(f"❌ Could not get button details: {e}")
                return False
            
            # Try different click methods
            print(f"\n🔄 Testing different click methods...")
            
            # Method 1: Standard click
            try:
                print("   Method 1: Standard click")
                avatar_button.click()
                time.sleep(2)
                print("   ✅ Standard click completed")
            except Exception as e:
                print(f"   ❌ Standard click failed: {e}")
            
            # Method 2: Force click
            try:
                print("   Method 2: Force click")
                avatar_button.click(force=True)
                time.sleep(2)
                print("   ✅ Force click completed")
            except Exception as e:
                print(f"   ❌ Force click failed: {e}")
            
            # Method 3: JavaScript click
            try:
                print("   Method 3: JavaScript click")
                self.page.evaluate("arguments[0].click();", avatar_button)
                time.sleep(2)
                print("   ✅ JavaScript click completed")
            except Exception as e:
                print(f"   ❌ JavaScript click failed: {e}")
            
            # Method 4: Mouse click at coordinates
            try:
                print("   Method 4: Mouse click at coordinates")
                box = avatar_button.bounding_box()
                if box:
                    x = box['x'] + box['width'] / 2
                    y = box['y'] + box['height'] / 2
                    self.page.mouse.click(x, y)
                    time.sleep(2)
                    print(f"   ✅ Mouse click at ({x}, {y}) completed")
                else:
                    print("   ❌ Could not get button position")
            except Exception as e:
                print(f"   ❌ Mouse click failed: {e}")
            
            print("\n🔍 Check if any of these clicks opened a file chooser dialog")
            print("   If not, the button might not be the actual upload trigger")
            
            return True
            
        except Exception as e:
            print(f"❌ Debug failed: {e}")
            return False

def main():
    """Main function to demonstrate Dreamina upload agent"""
    print("🎬 Dreamina Upload Agent - Starting...")
    
    # Create agent
    agent = DreaminaUploadAgent(headless=False)
    
    try:
        # Launch browser
        if not agent.launch_browser():
            print("❌ Failed to launch browser")
            return
        
        # Navigate directly to AI Avatar page
        if not agent.navigate_to_dreamina():
            print("❌ Failed to navigate to AI Avatar page")
            return
        
        print("\n✅ Successfully on AI Avatar page!")
        print("🔍 Please verify in the browser that you're on the AI Avatar upload interface.")
        
        # Show available files
        image_files, audio_files = agent.get_available_files()
        print(f"\n📁 Available files:")
        print(f"   Images: {len(image_files)}")
        print(f"   Audio: {len(audio_files)}")
        
        # Ask user what to do
        print("\n🎬 Upload Options:")
        print("1. Upload single file pair")
        print("2. Batch upload all files")
        print("3. Test upload with sample files")
        print("4. Just verify navigation (no upload)")
        print("5. Test Avatar button click only")
        print("6. Debug Avatar button (detailed analysis)")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            # Single upload
            image_path = input("Enter image path: ").strip()
            audio_path = input("Enter audio path: ").strip()
            
            if os.path.exists(image_path) and os.path.exists(audio_path):
                agent.upload_file_pair(image_path, audio_path)
            else:
                print("❌ File paths not found")
        
        elif choice == "2":
            # Batch upload
            max_files = input("Max files to upload (press Enter for all): ").strip()
            max_files = int(max_files) if max_files.isdigit() else None
            agent.batch_upload(max_files)
        
        elif choice == "3":
            # Test upload
            print("🧪 Testing upload with first available files...")
            if image_files and audio_files:
                test_image = image_files[0]['path']
                test_audio = audio_files[0]['path']
                agent.upload_file_pair(test_image, test_audio)
            else:
                print("❌ No test files available")
        
        elif choice == "4":
            # Just verify navigation
            print("✅ Navigation complete. Ready for manual upload testing.")
        
        elif choice == "5":
            # Test Avatar button click only
            agent.test_avatar_button_click()
        
        elif choice == "6":
            # Debug Avatar button
            agent.debug_avatar_button()
        
        else:
            print("❌ Invalid choice")
        
        # Keep browser open for inspection
        print("\n" + "=" * 50)
        print("BROWSER SESSION ACTIVE")
        print("=" * 50)
        print("Browser will stay open for inspection.")
        print("Press Ctrl+C to close.")
        print("=" * 50)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C. Closing...")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()

if __name__ == "__main__":
    main() 