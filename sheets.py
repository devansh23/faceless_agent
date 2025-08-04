import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

def get_sheet_data():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # Open the second worksheet (index 1)
    sheet = client.open_by_key(sheet_id).get_worksheet(1)
    data = sheet.get_all_records()

    result = []
    for idx, row in enumerate(data, start=1):
        line_no = str(idx).zfill(3)  # Use row number as line_no, zero-padded
        prompt = row.get("Image Prompt", "").strip()
        audio_link = row.get("Audio File", "").strip()
        reel_no = str(row.get("Reel #", "")).strip()

        if prompt and audio_link and reel_no:
            result.append({
                "line_no": line_no,
                "prompt": prompt,
                "audio_link": audio_link,
                "reel_no": reel_no
            })

    return result 