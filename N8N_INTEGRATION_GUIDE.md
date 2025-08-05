# N8N Integration Guide for WhatsApp Image Generation

## ✅ **Working Solution**

The WhatsApp image generation is now working perfectly! We've created a simple Python script that can be called from n8n to generate images using WhatsApp/ChatGPT.

## 📁 **Files Created**

- `generate_single_image_simple.py` - **Main script** (working perfectly)
- `whatsapp_image_api_agent_*.py` - API versions (have threading issues)

## 🚀 **How to Use with N8N**

### **Method 1: Execute Command Node (Recommended)**

This is the simplest and most reliable approach.

#### **N8N Configuration:**

1. **Add an "Execute Command" node** to your n8n workflow
2. **Configure the command:**

```bash
python3 /Users/devanshc/Documents/cursor\ projects/n8n_faceless_agent/generate_single_image_simple.py "{{ $json.reel_number }}" "{{ $json.snippet_number }}" "{{ $json.image_prompt }}"
```

#### **Input Data Format:**
```json
{
  "reel_number": "test",
  "snippet_number": "001", 
  "image_prompt": "A cozy Pixar-style 3D scene with a panda sitting on a couch"
}
```

#### **Output Handling:**
- **Success**: The script outputs `SUCCESS: /path/to/image.png`
- **Error**: The script outputs `ERROR: error message`

#### **N8N Response Parsing:**
Add a "Set" node after the Execute Command to parse the response:

```javascript
// Check if command was successful
const output = $('Execute Command').first().json.output;
const isSuccess = output.includes('SUCCESS:');

if (isSuccess) {
  // Extract file path
  const filePath = output.split('SUCCESS: ')[1].trim();
  return {
    success: true,
    file_path: filePath,
    reel_number: $json.reel_number,
    snippet_number: $json.snippet_number
  };
} else {
  // Extract error message
  const errorMessage = output.split('ERROR: ')[1] || 'Unknown error';
  return {
    success: false,
    error: errorMessage
  };
}
```

### **Method 2: HTTP Request Node (Alternative)**

If you prefer an API approach, you can create a simple HTTP server wrapper.

#### **Create a Simple HTTP Server:**

```python
# simple_http_server.py
from flask import Flask, request, jsonify
import subprocess
import sys
import os

app = Flask(__name__)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        reel_number = data['reel_number']
        snippet_number = data['snippet_number']
        image_prompt = data['image_prompt']
        
        # Call the script
        script_path = os.path.join(os.path.dirname(__file__), 'generate_single_image_simple.py')
        result = subprocess.run([
            sys.executable, script_path, 
            reel_number, snippet_number, image_prompt
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract file path from success output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if line.startswith('SUCCESS: '):
                    file_path = line.split('SUCCESS: ')[1]
                    return jsonify({
                        "success": True,
                        "file_path": file_path,
                        "reel_number": reel_number,
                        "snippet_number": snippet_number
                    })
        else:
            # Extract error from stderr
            error_msg = result.stderr.strip() or result.stdout.strip()
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

#### **N8N HTTP Request Configuration:**
- **Method**: `POST`
- **URL**: `http://localhost:5001/generate-image`
- **Headers**: `Content-Type: application/json`
- **Body**: 
```json
{
  "reel_number": "{{ $json.reel_number }}",
  "snippet_number": "{{ $json.snippet_number }}",
  "image_prompt": "{{ $json.image_prompt }}"
}
```

## 📋 **Complete N8N Workflow Example**

### **Workflow Steps:**

1. **Trigger Node** (Webhook/Manual)
2. **Set Node** - Prepare data:
   ```javascript
   return {
     reel_number: "test",
     snippet_number: "001",
     image_prompt: "A cozy Pixar-style 3D scene with a panda sitting on a couch"
   };
   ```
3. **Execute Command Node** - Run the script
4. **Set Node** - Parse response (see above)
5. **IF Node** - Check success/failure
6. **Success Branch** - Continue with workflow
7. **Error Branch** - Handle errors

### **Example Workflow JSON:**
```json
{
  "nodes": [
    {
      "parameters": {},
      "id": "webhook",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "reel_number",
              "value": "test"
            },
            {
              "name": "snippet_number", 
              "value": "001"
            },
            {
              "name": "image_prompt",
              "value": "A cozy Pixar-style 3D scene with a panda sitting on a couch"
            }
          ]
        }
      },
      "id": "set-data",
      "name": "Set Data",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "command": "python3 /Users/devanshc/Documents/cursor\\ projects/n8n_faceless_agent/generate_single_image_simple.py \"{{ $json.reel_number }}\" \"{{ $json.snippet_number }}\" \"{{ $json.image_prompt }}\""
      },
      "id": "execute-command",
      "name": "Execute Command",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "success",
              "value": "={{ $('Execute Command').first().json.output.includes('SUCCESS:') }}"
            },
            {
              "name": "file_path",
              "value": "={{ $('Execute Command').first().json.output.includes('SUCCESS:') ? $('Execute Command').first().json.output.split('SUCCESS: ')[1].trim() : '' }}"
            },
            {
              "name": "error",
              "value": "={{ $('Execute Command').first().json.output.includes('ERROR:') ? $('Execute Command').first().json.output.split('ERROR: ')[1] : '' }}"
            }
          ]
        }
      },
      "id": "parse-response",
      "name": "Parse Response",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.1,
      "position": [900, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Set Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Set Data": {
      "main": [
        [
          {
            "node": "Execute Command",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Execute Command": {
      "main": [
        [
          {
            "node": "Parse Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## ⚙️ **Prerequisites**

1. **Python Dependencies**: Install required packages:
   ```bash
   pip install playwright flask
   playwright install
   ```

2. **WhatsApp Setup**: 
   - Ensure WhatsApp Web is logged in
   - Have a "ChatGPT" contact pinned/available
   - The script will maintain the session automatically

3. **Directory Structure**: The script will create:
   ```
   /Users/devanshc/Desktop/ProteinPapaPanda/
   ├── {reel_number}/
   │   └── images/
   │       └── {snippet_number}.png
   ```

## 🔧 **Testing**

Test the script manually first:
```bash
python3 generate_single_image_simple.py test 001 "A simple red circle on white background"
```

Expected output:
```
SUCCESS: /Users/devanshc/Desktop/ProteinPapaPanda/test/images/001.png
```

## ⚠️ **Important Notes**

1. **Session Management**: The script uses persistent browser sessions, so WhatsApp Web must be logged in initially
2. **Timeout**: Image generation can take 2-10 minutes
3. **Error Handling**: The script detects common ChatGPT errors and handles them gracefully
4. **File Paths**: Ensure the target directory is writable
5. **Concurrent Usage**: Only one instance should run at a time to avoid conflicts

## 🎯 **Success Confirmation**

The script successfully:
- ✅ Accepts `reel_number`, `snippet_number`, and `image_prompt` as parameters
- ✅ Sends the prompt to WhatsApp/ChatGPT
- ✅ Waits for image generation (2-10 minutes)
- ✅ Downloads the generated image
- ✅ Saves it to `/Users/devanshc/Desktop/ProteinPapaPanda/{reel_number}/images/{snippet_number}.png`
- ✅ Returns success/error status for n8n integration

**Ready for n8n integration! 🚀** 