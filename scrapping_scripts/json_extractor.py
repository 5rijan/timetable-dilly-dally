import csv
import json
import re
from pathlib import Path

# Function to extract valid unit codes (e.g., ACCT2011)
def extract_unit_codes(text):
    if not text or text.lower() == "none":
        return []
    return re.findall(r"\b[A-Z]{4}\d{4}\b", text)

# Function to process the CSV and generate JSON files
def process_uos_csv(input_file, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize data structures for JSON outputs and error logging
    prohibition_data = {"nodes": [], "links": []}
    corequisite_data = {"nodes": [], "links": []}
    prerequisite_data = {"nodes": [], "links": []}
    error_log = []

    # Read the input CSV file
    with open(input_file, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                unit_code = row['Unit Code'].strip()
                title = row['Title'].strip()
                url = row['URL'].strip()
                description = row['Description'].strip()

                # Add the unit as a node to all datasets
                node = {"id": unit_code, "title": title, "url": url, "description": description}
                prohibition_data["nodes"].append(node)
                corequisite_data["nodes"].append(node)
                prerequisite_data["nodes"].append(node)

                # Process links for each type
                for category, dataset in [
                    ("Prohibitions", prohibition_data),
                    ("Corequisites", corequisite_data),
                    ("Prerequisites", prerequisite_data)
                ]:
                    linked_units = extract_unit_codes(row[category])
                    for target in linked_units:
                        dataset["links"].append({"source": unit_code, "target": target, "type": category.lower()})

            except Exception as e:
                error_log.append({
                    "unit_code": row.get('Unit Code', 'UNKNOWN'),
                    "error": str(e),
                    "row": row
                })

    # Write the JSON files
    with open(output_dir / "prohibition_uos.json", mode="w", encoding="utf-8") as f:
        json.dump(prohibition_data, f, indent=4)
    with open(output_dir / "corequisites_uos.json", mode="w", encoding="utf-8") as f:
        json.dump(corequisite_data, f, indent=4)
    with open(output_dir / "prerequisites_uos.json", mode="w", encoding="utf-8") as f:
        json.dump(prerequisite_data, f, indent=4)

    # Write the error log
    with open(output_dir / "error_log.json", mode="w", encoding="utf-8") as f:
        json.dump(error_log, f, indent=4)

# Example usage
input_csv = "data/uos_detailed.csv"
output_directory = "output"
process_uos_csv(input_csv, output_directory)
