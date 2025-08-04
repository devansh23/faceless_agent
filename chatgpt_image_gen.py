import os
from playwright.sync_api import sync_playwright
import time
import shutil

REFERENCE_IMAGE_PATH = "ppp_reference_image/ChatGPT Image Jul 12 2025 Vegetarian Protein Consumption.png"

def send_prompt_with_retry(page, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            input_box_selector = 'div[contenteditable="true"][data-tab="10"]'
            page.wait_for_selector(input_box_selector, timeout=10000)
            page.fill(input_box_selector, prompt)
            page.keyboard.press("Enter")
            print(f"Successfully sent prompt: {prompt[:40]}...")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retry
            else:
                print(f"Failed to send prompt after {max_retries} attempts")
                return False

def get_message_count_before_prompts(page):
    """Get the number of messages before sending prompts"""
    messages = page.query_selector_all(".message-in")
    return len(messages)

def get_images_after_prompts(page, message_count_before_prompts, expected_count):
    """
    Get images that were generated AFTER the prompts were sent
    Only considers images from messages that appeared after the initial count
    Returns the LAST N images (most recent ones)
    """
    print(f"🔍 Fetching images generated after prompts...")
    print(f"   Messages before prompts: {message_count_before_prompts}")
    
    # Get all messages
    all_messages = page.query_selector_all(".message-in")
    total_messages = len(all_messages)
    print(f"   Total messages now: {total_messages}")
    
    # Only consider messages that appeared AFTER we sent prompts
    new_messages = all_messages[message_count_before_prompts:]
    print(f"   New messages after prompts: {len(new_messages)}")
    
    # Extract images from new messages only
    new_images = []
    for i, bubble in enumerate(new_messages):
        img_elem = bubble.query_selector("img[src^='blob:']")
        if img_elem:
            img_src = img_elem.get_attribute('src')
            if img_src:
                new_images.append(img_src)
                print(f"   Found image {len(new_images)} in new message {message_count_before_prompts + i + 1}")
    
    print(f"   Total new images found: {len(new_images)}")
    
    # Check for error messages in new messages
    error_count = 0
    for i, bubble in enumerate(new_messages):
        # Look for common error indicators
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
                error_count += 1
                print(f"   ⚠️  Error detected in message {message_count_before_prompts + i + 1}: {indicator}")
                break
    
    if error_count > 0:
        print(f"   📊 Summary: {len(new_images)} images generated, {error_count} errors")
        print(f"   Expected: {expected_count} images, Actual: {len(new_images)} images")
    
    # Return the LAST N images (most recent ones)
    if len(new_images) >= expected_count:
        last_n_images = new_images[-expected_count:]
        print(f"   ✅ Taking last {expected_count} images (most recent)")
        return last_n_images
    else:
        print(f"   ⚠️  Only {len(new_images)} images available, returning all")
        return new_images

def download_image_by_src(page, img_src, save_path):
    try:
        img_elem = page.query_selector(f"img[src='{img_src}']")
        if not img_elem:
            print(f"Image not found with src {img_src}, trying fallback...")
            return False
        
        img_elem.click()
        download_btn_selector = 'span[data-icon="download-refreshed"]'
        page.wait_for_selector(download_btn_selector, timeout=20000)
        with page.expect_download() as download_info:
            page.click(download_btn_selector)
        download = download_info.value
        download_path = download.path()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        shutil.move(download_path, save_path)
        print(f"Saved image to {save_path}")
        page.keyboard.press("Escape")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def batch_generate_images_via_whatsapp(rows):
    whatsapp_url = "https://web.whatsapp.com/"
    chat_name = "ChatGPT"
    user_data_dir = os.path.abspath("whatsapp_session")
    downloads_dir = os.path.abspath(".whatsapp_downloads")
    prompts = []
    for row in rows:
        prompts.append({
            "prompt": row["prompt"],
            "line_no": row["line_no"],
            "reel_no": row["reel_no"]
        })

    context = None
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(user_data_dir, headless=False, accept_downloads=True, downloads_path=downloads_dir)
            page = context.new_page()
            page.goto(whatsapp_url)

            chat_selector = f"span[title='{chat_name}']"
            page.wait_for_selector(chat_selector, timeout=120000)
            page.click(chat_selector)

            # Get message count BEFORE sending any prompts
            print("📊 Recording initial chat state...")
            message_count_before_prompts = get_message_count_before_prompts(page)
            print(f"   Messages before prompts: {message_count_before_prompts}")

            # Send all prompts with error handling
            successful_prompts = []
            for idx, item in enumerate(prompts):
                print(f"Sending prompt {idx+1}/{len(prompts)}: {item['prompt'][:40]}")
                if send_prompt_with_retry(page, item["prompt"]):
                    successful_prompts.append(item)
                    time.sleep(10)
                else:
                    print(f"Failed to send prompt {idx+1}, stopping...")
                    break

            if not successful_prompts:
                print("No prompts were sent successfully. Exiting.")
                return

            print(f"✅ Successfully sent {len(successful_prompts)} prompts.")
            print(f"⏳ Waiting 10 minutes for images to be generated...")
            
            # Wait for 10 minutes (600 seconds)
            wait_time = 600
            for i in range(wait_time // 60):
                print(f"   {i+1}/10 minutes elapsed...")
                time.sleep(60)
            
            print("⏰ 10 minutes elapsed. Fetching images...")
            
            # Get images that were generated AFTER the prompts
            found_img_srcs = get_images_after_prompts(page, message_count_before_prompts, len(successful_prompts))

            if len(found_img_srcs) < len(successful_prompts):
                print(f"⚠️  Warning: Found {len(found_img_srcs)} images but expected {len(successful_prompts)}")
                print("   This might be due to ChatGPT errors or rate limiting")
                print("   Proceeding with available images...")
            elif len(found_img_srcs) > len(successful_prompts):
                print(f"⚠️  Warning: Found {len(found_img_srcs)} images but only sent {len(successful_prompts)} prompts")
                print("   Using first {len(successful_prompts)} images in order...")

            # Download images in order as images/<reel_no>/<line_no>.png
            successful_downloads = 0
            images_to_download = found_img_srcs[:len(successful_prompts)]  # Limit to expected count
            
            for idx, img_src in enumerate(images_to_download):
                reel_no = successful_prompts[idx]["reel_no"]
                line_no = successful_prompts[idx]["line_no"]
                save_dir = os.path.join("images", str(reel_no))
                image_path = os.path.join(save_dir, f"{line_no}.png")
                
                print(f"Downloading image {idx+1}/{len(images_to_download)} for reel {reel_no}, line {line_no}")
                if download_image_by_src(page, img_src, image_path):
                    successful_downloads += 1
                else:
                    print(f"Failed to download image for {reel_no}/{line_no}")

            print(f"🎉 Downloaded {successful_downloads}/{len(images_to_download)} images successfully")

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if context:
            print("\n" + "="*50)
            print("SCRIPT COMPLETED - BROWSER WILL STAY OPEN")
            print("="*50)
            print("The browser will remain open for your inspection.")
            print("To close the browser, manually close the browser window.")
            print("To exit this script, press Ctrl+C in the terminal.")
            print("="*50)
            
            try:
                # Keep the script running indefinitely
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived Ctrl+C. Exiting...")
                try:
                    context.close()
                    print("Browser closed successfully.")
                except Exception as e:
                    print(f"Browser close error (ignored): {e}")

if __name__ == "__main__":
    from sheets import get_sheet_data
    rows = get_sheet_data()
    batch_generate_images_via_whatsapp(rows) 