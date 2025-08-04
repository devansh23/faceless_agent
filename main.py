from sheets import get_sheet_data
# import os
# from dotenv import load_dotenv
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# from chatgpt_image_gen import generate_image
# from audio_downloader import download_audio
# from dreamina_uploader import upload_to_dreamina

def main():
    rows = get_sheet_data()
    for row in rows:
        print(row)
    # for row in rows:
    #     line_no = row["line_no"]
    #     prompt = row["prompt"]
    #     audio_url = row["audio_link"]
    #     generate_image(prompt, line_no)
    #     download_audio(audio_url, line_no)
    #     upload_to_dreamina(f"images/{line_no}.png", f"audio/{line_no}.mp3")

if __name__ == "__main__":
    main()