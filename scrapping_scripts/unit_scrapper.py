import requests
import csv
import re
import json  # Correct module for JSON parsing

# URL with all results in JSON format
url = "https://www.sydney.edu.au/s/search.html?query=a&collection=Sydney-Curriculum_UOS&profile=_default_preview&form=custom-json&num_ranks=6658"

# Function to clean invalid escape sequences
def clean_json_response(response_text):
    # Replace invalid escape sequences
    cleaned_text = re.sub(r'\\[^"\\/bfnrtu]', '', response_text)
    return cleaned_text

# Function to fetch and save results
def fetch_and_save_results(url, output_file):
    # Make the request to the API
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")
        return
    
    # Clean the response text
    cleaned_text = clean_json_response(response.text)

    # Parse JSON response
    try:
        data = json.loads(cleaned_text)  # Use the correct JSON module
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
        with open("response_debug.html", "w", encoding="utf-8") as debug_file:
            debug_file.write(cleaned_text)  # Save the raw response for inspection
        print("Saved cleaned response to 'response_debug.html'.")
        return
    
    results = data.get("results", [])
    
    # Open CSV file for writing
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header row
        writer.writerow(["Unit Code", "Title", "URL", "Description"])
        
        # Write each result
        for result in results:
            uos_code = result.get("uosCode", "N/A")
            title = result.get("title", "N/A")
            url = result.get("UoSURL", "N/A")
            description = result.get("description", "N/A")
            writer.writerow([uos_code, title, url, description])

    print(f"Results saved to {output_file}")

# Call the function with the provided URL
output_csv = "unit_search_results_full.csv"
fetch_and_save_results(url, output_csv)
