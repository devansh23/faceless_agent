#!/usr/bin/env python3
"""
Add test data to Google Sheets for API testing
"""

import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

def add_test_data():
    """Add test data to Google Sheets"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # Open the second worksheet (index 1)
    sheet = client.open_by_key(sheet_id).get_worksheet(1)
    
    # Test data to add
    test_data = [
        ["Reel #", "Image Prompt", "Audio File"],
        ["1", "A simple red circle on white background", "https://drive.google.com/file/d/test1"],
        ["1", "A blue square with rounded corners", "https://drive.google.com/file/d/test2"],
        ["1", "A green triangle pointing up", "https://drive.google.com/file/d/test3"],
        ["2", "A yellow star with 5 points", "https://drive.google.com/file/d/test4"],
        ["2", "A purple heart shape", "https://drive.google.com/file/d/test5"],
        ["3", "A black cat sitting on a windowsill", "https://drive.google.com/file/d/test6"],
        ["3", "A white dog running in a park", "https://drive.google.com/file/d/test7"],
        ["3", "A brown bird flying in the sky", "https://drive.google.com/file/d/test8"]
    ]
    
    # Clear existing data and add test data
    sheet.clear()
    sheet.update('A1', test_data)
    
    print("✅ Test data added to Google Sheets!")
    print("Available reel numbers: 1, 2, 3")
    print("You can now test the API with these reel numbers.")

if __name__ == "__main__":
    add_test_data() 