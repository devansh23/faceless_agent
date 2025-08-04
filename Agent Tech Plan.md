
# Technical Implementation Plan: Video Asset Automation Agent (MVP)

## 🎯 Goal
Automate the creation and upload of image-audio pairs for avatar video generation using:
- Google Sheets
- ChatGPT (via browser)
- Google Drive
- Dreamina (via browser)

---

## 📦 Folder Structure

```
video-agent/
├── main.py                    # Entry point
├── config.py                  # Global config/paths
├── sheets.py                  # Google Sheets read logic
├── chatgpt_image_gen.py       # Playwright script for ChatGPT image generation
├── audio_downloader.py        # Google Drive audio fetcher
├── dreamina_uploader.py       # Playwright script for Dreamina upload
├── utils.py                   # Helper functions
├── .env                       # Environment variables (local only)
├── requirements.txt
```

---

## 🛠️ Modules & Responsibilities

### 1. `sheets.py`
- Uses Google service account to read a shared sheet
- Returns rows like:
```python
[
  {"line_no": "001", "prompt": "man walking", "audio_link": "https://..."},
  ...
]
```

### 2. `chatgpt_image_gen.py`
- Uses Playwright to log into ChatGPT via browser
- Sends the image prompt
- Waits for image generation
- Downloads the image as `images/<line_no>.png`

### 3. `audio_downloader.py`
- Takes a Google Drive link and extracts the file ID
- Downloads the audio using public access link
- Saves as `audio/<line_no>.mp3`

### 4. `dreamina_uploader.py`
- Uses Playwright to log into Dreamina
- Uploads the image + audio
- Triggers avatar generation

### 5. `main.py`
- Orchestration of the above steps in order

---

## 🧪 Test Scenarios

- ✅ `get_sheet_data()` returns correct rows
- ✅ Image downloads after prompt submitted to ChatGPT
- ✅ Audio saves locally from shared Google Drive link
- ✅ Dreamina receives correct upload and starts render

---

## 🔁 Fallback Plan: WhatsApp ChatGPT

If ChatGPT UI becomes unstable:
- Automate WhatsApp Web via Playwright/Selenium
- Send prompt to saved ChatGPT bot contact
- Screenshot the response and save it as the image

---

## 🔐 Secrets & Auth

Store in `.env`:
```
GOOGLE_SHEET_ID=
CHATGPT_EMAIL=
CHATGPT_PASSWORD=
DREAMINA_EMAIL=
DREAMINA_PASSWORD=
```

---

## 💰 Cost Considerations

| Component     | Cost        |
|---------------|-------------|
| ChatGPT (UI)  | Free        |
| Google APIs   | Free Tier   |
| Playwright    | Free        |
| Dreamina      | Variable    |
| WhatsApp Bot  | Free/manual |

---

## 🧭 First Cursor Prompt

1. Drop in the PRD
2. Then say:

> “Here is my architecture and technical execution plan for the agent I want to build. Use this context as we build each component. First, help me implement `sheets.py` to read rows from Google Sheet using a service account.”
