#!/usr/bin/env python3
"""
Audio Download API server wrapper
Provides a clean API endpoint for n8n integration to download audio files by reel
"""

from flask import Flask, request, jsonify
import subprocess
import sys
import os
import logging
import threading
import queue
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global queue for handling concurrent requests
request_queue = queue.Queue()
processing_lock = threading.Lock()
is_processing = False

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
                logger.info(f"Processing audio download request for reel: {reel_number}")
                
                # Call the audio download script
                script_path = os.path.join(os.path.dirname(__file__), 'download_reel_audio.py')
                result = subprocess.run([
                    sys.executable, script_path, str(reel_number)
                ], capture_output=True, text=True, timeout=600)  # 10 minutes timeout
                
                # Store result for the waiting thread
                request_data['result'] = result
                request_data['completed'] = True
                
            except Exception as e:
                logger.error(f"Error processing audio download request: {e}")
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
        "message": "Audio Download API is running",
        "timestamp": "2025-08-05T17:50:00.000000",
        "queue_size": queue_size,
        "is_processing": is_processing
    })

@app.route('/download-reel-audio', methods=['POST'])
def download_reel_audio():
    """Download audio files for a reel endpoint"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        if 'reel_number' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: reel_number"
            }), 400
        
        reel_number = data['reel_number']
        
        # Validate data type
        if not isinstance(reel_number, (int, str)):
            return jsonify({
                "success": False,
                "error": "reel_number must be a number or string"
            }), 400
        
        logger.info(f"Received audio download API request for reel: {reel_number}")
        
        # Create request data
        request_data = {
            'reel_number': reel_number,
            'completed': False,
            'result': None,
            'error': None
        }
        
        # Add to queue
        request_queue.put(request_data)
        logger.info(f"Audio download request queued. Queue size: {request_queue.qsize()}")
        
        # Wait for completion (with timeout)
        timeout = 600  # 10 minutes total timeout
        start_time = time.time()
        
        while not request_data['completed'] and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        if not request_data['completed']:
            return jsonify({
                "success": False,
                "error": "Request timed out after 10 minutes"
            }), 408
        
        # Check for processing error
        if request_data['error']:
            return jsonify({
                "success": False,
                "error": request_data['error']
            }), 500
        
        # Process result
        result = request_data['result']
        if result.returncode == 0:
            # Extract success message from output
            output_lines = result.stdout.strip().split('\n')
            success_line = None
            for line in output_lines:
                if line.startswith('SUCCESS: '):
                    success_line = line
                    break
            
            if success_line:
                logger.info(f"Audio files downloaded successfully for reel {reel_number}")
                return jsonify({
                    "success": True,
                    "reel_number": reel_number,
                    "message": success_line,
                    "details": "Audio files downloaded and saved to organized folder structure",
                    "audio_directory": f"/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/Audio"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Script completed but no success message found",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }), 500
        else:
            # Extract error from stderr or stdout
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Audio download script failed: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
            
    except Exception as e:
        logger.error(f"Audio download API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("Starting Audio Download API Server...")
    logger.info("API will be available at: http://localhost:5002")
    logger.info("Endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /download-reel-audio - Download audio files for a reel")
    logger.info("Queue system enabled - requests will be processed sequentially")
    app.run(host='0.0.0.0', port=5002, debug=False) 