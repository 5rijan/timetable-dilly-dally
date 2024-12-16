import requests
import json  # Import for pretty printing JSON

# API Endpoint
url = "https://timetable.sydney.edu.au/odd/rest/timetable/subjects"

# Request payload (data sent in the POST request)
payload = {
    "search-term": "COMP2017",
    "semester": ["S1C", "S1CG", "S1CIAP", "S1CIMR", "S2C"],
    "campus": "ALL",
    "faculty": "ALL",
    "type": "ALL",
    "days": ["1"],
    "start-time": "00:00",
    "end-time": "22:00"
}

# Headers (if needed)
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "YourAppName/1.0" 
}

# Sending the POST request
response = requests.post(url, data=payload, headers=headers)

# Check the response
if response.status_code == 200:
    print("Request successful!")
    
    # Parse and pretty-print the JSON response
    try:
        json_data = response.json()  # Parse JSON
        pretty_json = json.dumps(json_data, indent=4)  # Convert to pretty-printed string
        print(pretty_json)
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
else:
    print(f"Failed to fetch data: {response.status_code}")
    print(response.text)
