
# PRD: Video Asset Automation Agent (MVP)

## Overview

We are building a system that enables efficient, high-quality, scalable video content generation. The current scope focuses on building an agent that:

1. Reads media prompts and audio file links from a Google Sheet.
2. Uses ChatGPT’s *browser UI* (not API) to generate images from prompts.
3. Downloads both images and audio files to local directories.
4. Uploads these paired assets to **Dreamina** for AI avatar video generation.

This MVP is a small but vital piece of a larger vision to scale distribution-first, high-quality video content across domains and formats.

---

## Goals (MVP Scope)

Build an agent that:

- Authenticates into a Google Sheet
- For each row:
  - Takes the image prompt
  - Opens ChatGPT in a browser (via automation), enters the prompt, and downloads the generated image
  - Takes the audio file URL (hosted on Google Drive), downloads it
  - Uploads the image + audio pair to Dreamina via its web interface

---

## User Stories

### US1: Script-to-Media Agent
**As a** content creator,  
**I want to** enter script lines and prompts in a Google Sheet,  
**So that** an agent can generate image assets and download audio files.

### US2: Image Generation via ChatGPT UI
**As a** builder,  
**I want to** use ChatGPT in the browser for generating images,  
**So that** I avoid using OpenAI APIs and stick to manual-gen style outputs.

### US3: Dreamina Upload Automation
**As a** creator,  
**I want to** automatically upload image-audio pairs to Dreamina,  
**So that** I can rapidly generate avatar-style videos with minimal effort.

---

## Functional Requirements

### 1. **Google Sheet Integration**
- Read a Google Sheet (user will configure access)
- Each row contains:
  - Line number
  - Image prompt
  - Audio file URL (Google Drive link)

### 2. **ChatGPT Image Generation (via Browser Automation)**
- Agent opens ChatGPT (credentials provided)
- Pastes the prompt from the Google Sheet
- Waits for image generation to complete
- Downloads the image with filename: `<line_number>.png`
- Saves to a designated local folder: `/images`

> **Important**: Must simulate a real user using browser automation (e.g. Playwright/Puppeteer)

### 3. **Audio Download**
- For each row, extract the audio URL (from Google Drive)
- Download the audio file as `<line_number>.mp3`
- Save to `/audio`

### 4. **Dreamina Upload (via Browser Automation)**
- Log into [Dreamina](https://dreamina.ai) (credentials provided)
- For each line:
  - Upload corresponding image and audio file
  - Trigger avatar generation workflow

---

## Non-Functional Requirements

- **Reliability**: Should gracefully handle failed downloads or site load failures (retry mechanism)
- **Performance**: Should work on batch prompts; sequential processing is acceptable for now
- **Security**: Store credentials securely or allow for manual session handling

---

## Technical Constraints

- No use of OpenAI API for image generation
- Must work with Google Sheet + Google Drive
- Browser-based automation for ChatGPT and Dreamina (headless optional but not required)

---

## Directories

```
/project-root
  /images     ← downloaded images from ChatGPT UI
  /audio      ← downloaded mp3 files from Google Drive
  /logs       ← task success/failure logs (optional for debugging)
```

---

## Inputs & Outputs

| Source         | Type     | Example Output                         |
|----------------|----------|----------------------------------------|
| Google Sheet   | Text     | Prompt: `A man walking in the desert` |
| Google Drive   | URL      | Audio: `https://drive.google.com/...` |
| ChatGPT        | Image UI | `images/001.png`                      |
| Dreamina       | Web UI   | Avatar video gets triggered via upload|

---

## Milestone Plan

| Phase          | Deliverable                           |
|----------------|----------------------------------------|
| Phase 1        | Google Sheet integration               |
| Phase 2        | ChatGPT image generation (via browser) |
| Phase 3        | Audio file download                    |
| Phase 4        | Dreamina upload automation             |
| Phase 5        | CLI trigger / n8n trigger integration (optional)|

---

## Appendix

### 🌄 Long-Term Vision

- Build a fully autonomous video generation pipeline from script → chunking → media generation → stitching.
- Media includes:
  - Voiceovers (11 Labs)
  - Sound effects and background music
  - Relevant visuals (images, stock video, animation)
  - On-screen text, slides, and motion design
- Script chunking will be semantically and rhythmically informed—mimicking a director's creative judgment.
- System should evolve to automate final assembly/editing or hand off files in a structured format to editors.
- Goal is to scale high-quality short-form videos across themes, domains, and niches.
- Monetization and distribution strategy will follow once we validate scale and quality output.

### 📱 Reference Apps

- **Real Charts**
- **Flick TV**

These platforms validate the hunger for strong short-format storytelling, powered by writing + visuals + voice.

---

## Auth & Access

- Google Sheet access: via service account or OAuth
- ChatGPT access: via manual login or scriptable login (cookie/session preferred)
- Dreamina access: credentials to be manually configured

---

## Out of Scope

- Final video stitching/assembly
- Semantic chunking of scripts
- Monetization, analytics, and distribution mechanisms

---

## Notes

- You run n8n locally via Docker with a GUI
- The agent will operate independently of n8n but could be triggered via it later
