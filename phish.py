import requests
import os
import re
import time

BASE_URL = "https://phish.in/download-track/"
START = 3
END = 36829
WEBSITE_NAME = "phish.in"
BASE_SAVE_DIR = f"./{WEBSITE_NAME}/"
MAX_RETRIES = 5

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
}

def extract_filename_from_headers(headers):
    content_disposition = headers.get('Content-Disposition', '')
    matches = re.findall('filename="(.+)"', content_disposition)
    return matches[0] if matches else None

def log_failure(url):
    with open("log.txt", "a") as log_file:
        log_file.write(f"Failed to download: {url}\n")

for i in range(START, END + 1):
    print(f"Processing track {i} of {END}")
    url = BASE_URL + str(i).zfill(5)
    
    retries = 0
    success = False
    
    while retries < MAX_RETRIES and not success:
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                original_filename = extract_filename_from_headers(response.headers)
                if original_filename:
                    year_match = re.search(r"(\d{4})-\d{2}-\d{2}", original_filename)
                    if year_match:
                        year = year_match.group(1)
                        year_dir = os.path.join(BASE_SAVE_DIR, year)
                        if not os.path.exists(year_dir):
                            os.makedirs(year_dir)
                        file_path = os.path.join(year_dir, original_filename)
                    else:
                        print(f"Failed to extract year from filename: {original_filename}")
                        file_path = os.path.join(BASE_SAVE_DIR, original_filename)
                    print(f"Saving '{original_filename}' to '{file_path}'")

                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=1024):
                            file.write(chunk)
                    
                    
                    file_size = os.path.getsize(file_path) / 1024
                    print(f"Saved {file_size:.2f} KB to {file_path}")
                    success = True
                else:
                    print(f"Failed to extract filename for track {i}")
                    log_failure(url)
                    retries += 1
            else:
                print(f"Failed to download track {i}. Status code: {response.status_code}")
                log_failure(url)
                retries += 1
        except Exception as e:
            print(f"Error while downloading track {i}. Error: {e}")
            log_failure(url)
            retries += 1
        

        if not success:
            time.sleep(5)

    # Respectful scraping delay
    time.sleep(2)
