#!/usr/bin/env python3
"""
ChatGPT Image Generation API Server (via WhatsApp Web)

Exposes endpoints to batch-generate images using the WhatsApp Web ChatGPT chat.
Implements the batching logic from `chatgpt_image_gen.py` without keeping the
browser open indefinitely.

Endpoints:
  - GET  /health
  - POST /batch-generate-images
      Body options:
        1) { "rows": [{"prompt": str, "line_no": str|int, "reel_no": str|int}, ...], "wait_minutes"?: int }
        2) { "reel_number": str|int, "wait_minutes"?: int }
           Will fetch prompts from Google Sheets using `sheets.get_prompts_by_reel`.
"""

from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os
import time
import shutil
import logging
from datetime import datetime

try:
    # Optional import; only needed when using reel_number fetch
    from sheets import get_prompts_by_reel
except Exception:
    get_prompts_by_reel = None

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============ Core WhatsApp helpers (adapted from chatgpt_image_gen.py) ============

def send_prompt_with_retry(page, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            input_box_selector = 'div[contenteditable="true"][data-tab="10"]'
            page.wait_for_selector(input_box_selector, timeout=10000)
            page.fill(input_box_selector, prompt)
            page.keyboard.press("Enter")
            logger.info(f"Successfully sent prompt: {prompt[:80]}...")
            return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error(f"Failed to send prompt after {max_retries} attempts")
                return False


def get_message_count_before_prompts(page):
    messages = page.query_selector_all(".message-in")
    return len(messages)


def get_images_after_prompts(page, message_count_before_prompts, expected_count):
    logger.info("Fetching images generated after prompts...")
    all_messages = page.query_selector_all(".message-in")
    new_messages = all_messages[message_count_before_prompts:]

    new_images = []
    for bubble in new_messages:
        img_elem = bubble.query_selector("img[src^='blob:']")
        if img_elem:
            img_src = img_elem.get_attribute('src')
            if img_src:
                new_images.append(img_src)

    # Basic error detection in new messages
    error_indicators = [
        "Sorry, I can't generate that image",
        "I'm unable to create this image",
        "Error generating image",
        "Unable to process",
        "Sorry, I can't do that"
    ]
    error_count = 0
    for bubble in new_messages:
        try:
            message_text = (bubble.inner_text() or "").lower()
        except Exception:
            message_text = ""
        for indicator in error_indicators:
            if indicator.lower() in message_text:
                error_count += 1
                break

    if error_count:
        logger.warning(f"Detected {error_count} error message(s) after prompts")

    if len(new_images) >= expected_count:
        return new_images[-expected_count:]
    return new_images


def download_image_by_src(page, img_src, save_path):
    try:
        img_elem = page.query_selector(f"img[src='{img_src}']")
        if not img_elem:
            logger.warning(f"Image not found with src {img_src}")
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
        logger.info(f"Saved image to {save_path}")
        page.keyboard.press("Escape")
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def download_image_from_element(page, img_elem, save_path):
    """Download image by clicking a given image element and using the viewer's download button."""
    try:
        if not img_elem:
            logger.warning("download_image_from_element called with None element")
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
        logger.info(f"Saved image to {save_path}")
        page.keyboard.press("Escape")
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Download failed from element: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False

def _scroll_chat_up(page):
    """Attempt to scroll the chat upwards to load older messages.
    Tries multiple strategies to be robust against DOM changes.
    """
    try:
        # Click into the chat area so keyboard events apply there
        try:
            page.click("div[role='application']", timeout=2000)
        except Exception:
            pass

        # Strategy 1: PageUp
        try:
            page.keyboard.press("PageUp")
            return True
        except Exception:
            pass

        # Strategy 2: Scroll the likely message list container
        selectors = [
            "div[aria-label='Message list']",
            "div[data-testid='conversation-panel-body']",
            "div#main div[tabindex='-1']",
        ]
        for sel in selectors:
            try:
                page.eval_on_selector(sel, "el => el.scrollBy(0, -800)")
                return True
            except Exception:
                continue

        # Strategy 3: Wheel event
        try:
            page.mouse.wheel(0, -800)
            return True
        except Exception:
            pass
    except Exception:
        pass
    return False


def _collect_last_n_image_srcs_with_scrolling(page, n, max_scrolls=120):
    """Collect last n image srcs by scanning from bottom and scrolling up as needed."""
    images_collected = []
    seen = set()
    scrolls = 0

    while len(images_collected) < n and scrolls <= max_scrolls:
        try:
            bubbles = page.query_selector_all(".message-in")
            # Iterate from bottom to top
            for bubble in reversed(bubbles):
                try:
                    img_elem = bubble.query_selector("img[src^='blob:']")
                except Exception:
                    img_elem = None
                if not img_elem:
                    continue
                try:
                    img_src = img_elem.get_attribute('src')
                except Exception:
                    img_src = None
                if not img_src:
                    continue
                if img_src in seen:
                    continue
                seen.add(img_src)
                images_collected.append(img_src)
                if len(images_collected) >= n:
                    break
        except Exception as _:
            pass

        if len(images_collected) >= n:
            break

        # Scroll up and try to load more
        _scroll_chat_up(page)
        scrolls += 1
        time.sleep(0.5)

    return images_collected[:n]


def run_batch_in_whatsapp(rows, wait_minutes=10):
    """Core batch flow:
    - Opens WhatsApp Web (persistent session)
    - Sends all prompts
    - Waits `wait_minutes`
    - Collects the most recent N images and downloads them in order to images/<reel>/<line>.png
    Returns a summary dict.
    """
    whatsapp_url = "https://web.whatsapp.com/"
    chat_name = "ChatGPT"
    user_data_dir = os.path.abspath("whatsapp_session")
    downloads_dir = os.path.abspath(".whatsapp_downloads")

    prompts = []
    for row in rows:
        prompts.append({
            "prompt": row["prompt"],
            "line_no": str(row["line_no"]),
            "reel_no": str(row["reel_no"]),
        })

    sent = 0
    downloaded = 0
    errors = []

    playwright_instance = None
    context = None

    try:
        playwright_instance = sync_playwright().start()
        context = playwright_instance.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            accept_downloads=True,
            downloads_path=downloads_dir,
        )
        page = context.new_page()
        page.goto(whatsapp_url)

        chat_selector = f"span[title='{chat_name}']"
        page.wait_for_selector(chat_selector, timeout=120000)
        page.click(chat_selector)

        # Record initial message count
        message_count_before_prompts = get_message_count_before_prompts(page)

        # Send all prompts
        successful_prompts = []
        for item in prompts:
            if send_prompt_with_retry(page, item["prompt"]):
                successful_prompts.append(item)
                sent += 1
                time.sleep(10)
            else:
                errors.append({"type": "send_failed", "item": item})
                break

        if not successful_prompts:
            return {
                "success": False,
                "message": "No prompts were sent successfully.",
                "sent": 0,
                "downloaded": 0,
                "errors": errors,
                "results": [],
            }

        # Post-wait bottom-up retrieval with scrolling
        logger.info("Collecting last N images by scrolling up from the bottom and downloading immediately...")
        expected = len(successful_prompts)
        next_prompt_index = expected - 1
        seen_srcs = set()
        results = []
        scrolls = 0
        max_scrolls = 200

        while next_prompt_index >= 0 and scrolls <= max_scrolls:
            try:
                bubbles = page.query_selector_all(".message-in")
                # Iterate bottom to top
                for bubble in reversed(bubbles):
                    if next_prompt_index < 0:
                        break
                    try:
                        img_elem = bubble.query_selector("img[src^='blob:']")
                    except Exception:
                        img_elem = None
                    if not img_elem:
                        continue
                    try:
                        img_src = img_elem.get_attribute('src')
                    except Exception:
                        img_src = None
                    if img_src and img_src in seen_srcs:
                        continue

                    reel_no = successful_prompts[next_prompt_index]["reel_no"]
                    line_no = successful_prompts[next_prompt_index]["line_no"]
                    save_dir = os.path.join("images", str(reel_no))
                    image_path = os.path.join(save_dir, f"{line_no}.png")

                    ok = download_image_from_element(page, img_elem, image_path)
                    if ok:
                        downloaded += 1
                        next_prompt_index -= 1
                    results.append({
                        "reel_no": reel_no,
                        "line_no": line_no,
                        "downloaded": ok,
                        "file_path": image_path if ok else None,
                    })
                    if img_src:
                        seen_srcs.add(img_src)

                    if next_prompt_index < 0:
                        break

                if next_prompt_index < 0:
                    break

                # Scroll up to load older messages
                _scroll_chat_up(page)
                scrolls += 1
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Error during bottom-up download loop: {e}")
                time.sleep(0.5)

        remaining = next_prompt_index + 1
        if remaining > 0:
            logger.warning(f"Bottom-up retrieval ended with {remaining} image(s) still missing after scrolling.")

        return {
            "success": downloaded == expected,
            "message": f"Downloaded {downloaded}/{expected} images via bottom-up scrolling immediate downloads.",
            "sent": sent,
            "downloaded": downloaded,
            "results": results,
            "missing": remaining if remaining > 0 else 0,
        }

    except Exception as e:
        logger.exception("Batch run failed")
        return {
            "success": False,
            "message": f"Error during execution: {e}",
            "sent": sent,
            "downloaded": downloaded,
            "errors": errors + [{"type": "exception", "error": str(e)}],
            "results": [],
        }
    finally:
        try:
            if context:
                context.close()
        except Exception:
            pass
        try:
            if playwright_instance:
                playwright_instance.stop()
        except Exception:
            pass


# ============ Flask endpoints ============

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "ChatGPT Image Generation API is running",
        "timestamp": datetime.now().isoformat(),
    })


@app.route('/batch-generate-images', methods=['POST'])
def batch_generate_images():
    try:
        data = request.get_json(force=True)
        wait_minutes = int(data.get('wait_minutes', 10))

        rows = data.get('rows')
        reel_number = data.get('reel_number')

        if rows is None and reel_number is None:
            return jsonify({
                "success": False,
                "error": "Provide either 'rows' or 'reel_number' in request body"
            }), 400

        prepared_rows = []

        if rows is not None:
            if not isinstance(rows, list) or len(rows) == 0:
                return jsonify({
                    "success": False,
                    "error": "'rows' must be a non-empty list"
                }), 400
            for i, row in enumerate(rows):
                if not isinstance(row, dict):
                    return jsonify({
                        "success": False,
                        "error": f"Row {i} must be an object"
                    }), 400
                for field in ["prompt", "line_no", "reel_no"]:
                    if field not in row:
                        return jsonify({
                            "success": False,
                            "error": f"Row {i} missing required field: {field}"
                        }), 400
                prepared_rows.append({
                    "prompt": str(row["prompt"]).strip(),
                    "line_no": str(row["line_no"]).zfill(3) if str(row["line_no"]).isdigit() else str(row["line_no"]),
                    "reel_no": str(row["reel_no"]).strip(),
                })

        if prepared_rows == [] and reel_number is not None:
            if get_prompts_by_reel is None:
                return jsonify({
                    "success": False,
                    "error": "Google Sheets integration not available in this environment"
                }), 400
            prompts = get_prompts_by_reel(reel_number)
            if not prompts:
                return jsonify({
                    "success": False,
                    "error": f"No prompts found for reel_number={reel_number}"
                }), 404
            for p in prompts:
                prepared_rows.append({
                    "prompt": p["prompt"],
                    "line_no": p.get("line_no") or str(p.get("image_number", "1")).zfill(3),
                    "reel_no": str(reel_number),
                })

        summary = run_batch_in_whatsapp(prepared_rows, wait_minutes=wait_minutes)
        status_code = 200 if summary.get("success") else 500
        return jsonify(summary), status_code

    except Exception as e:
        logger.exception("API error")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {e}"
        }), 500


if __name__ == '__main__':
    logger.info("Starting ChatGPT Image Generation API Server...")
    logger.info("API will be available at: http://localhost:5003")
    logger.info("Endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /batch-generate-images - Batch generate images from rows or a reel number")
    app.run(host='0.0.0.0', port=5003, debug=False)


