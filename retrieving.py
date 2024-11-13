import requests
import json
import os
chapter_urls = [
    "http://127.0.0.1:8000/extract/1",
    "http://127.0.0.1:8000/extract/2",
    "http://127.0.0.1:8000/extract/3",
    "http://127.0.0.1:8000/extract/4",
    "http://127.0.0.1:8000/extract/5"
]
all_chapters_data = {}

# Loop through each chapter URL
for url in chapter_urls:
    # Make a GET request to the endpoint
    response = requests.get(url, timeout= 10)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        chapter_content = data['Content']
        print(f"Extracted Content for {url}:")
        print(chapter_content)

        # Store the extracted content in the dictionary
        chapter_number = url.split("/")[-1]  # Get the chapter number from the URL
        all_chapters_data[chapter_number] = {
            "Extracted Content": chapter_content
        }
    else:
        print(f"Failed to retrieve content from {url}: {response.status_code}")

# Define the JSON file path
json_file_path = "C:\\Users\\Crich Joved\\OneDrive\\Desktop\\Fast API\\retrieving_data\\extracted_content.json"
os.makedirs(os.path.dirname(json_file_path), exist_ok=True) 

# Write the dictionary to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(all_chapters_data, json_file, indent=4)

print(f"\nAll chapter data has been written to {json_file_path}")