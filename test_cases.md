# ✅ Test Scenarios for MVP Agent

### ✅ Test Case 1: Sheet Access
- [ ] Validate that `get_sheet_data()` returns rows with `line_no`, `prompt`, `audio_link`.

### ✅ Test Case 2: ChatGPT Image Generation
- [ ] Enter prompt manually into ChatGPT UI, test Playwright saves the generated image to `images/<line_no>.png`.

### ✅ Test Case 3: Audio File Download
- [ ] Test `download_audio()` with a public Google Drive audio URL. Ensure it saves as `audio/<line_no>.mp3`.

### ✅ Test Case 4: Dreamina Upload
- [ ] Use `upload_to_dreamina()` with test image/audio. Validate upload success manually.

---

## 🔁 If ChatGPT UI is unreliable

### ✅ Backup: WhatsApp Automation Flow
- [ ] If ChatGPT UI fails, fallback to sending prompts via WhatsApp to ChatGPT bot contact.
- [ ] WhatsApp API or Selenium automation can simulate sending messages to bot contact.
- [ ] Capture screenshot or response image and save as `images/<line_no>.png`.

> 📌 This is a last-resort backup and will require setting up WhatsApp Web login persistence in Playwright or Selenium.
