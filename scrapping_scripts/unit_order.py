import csv
import json
import time
from tqdm import tqdm

def process_csv(input_file, output_file, log_file):
    start_time = time.time()

    # Read the CSV file
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Sort rows by Unit Code
    rows.sort(key=lambda x: x['Unit Code'])

    # Initialize structure for duplicate Unit Codes
    duplicate_unit_codes = []

    # Identify duplicates with a progress bar
    seen_unit_codes = set()
    for row in tqdm(rows, desc="Processing rows", unit="row"):
        unit_code = row['Unit Code']
        if unit_code in seen_unit_codes:
            duplicate_unit_codes.append(unit_code)
        else:
            seen_unit_codes.add(unit_code)

    # Write the sorted rows to the output CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write duplicates to a JSON log file
    with open(log_file, 'w', encoding='utf-8') as jsonfile:
        json.dump({"duplicate_unit_codes": duplicate_unit_codes}, jsonfile, indent=4)

    # End and print elapsed time
    elapsed_time = time.time() - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    input_csv = "updated.csv"  
    output_csv = "final.csv"  
    duplicate_log = "duplicates.json"

    process_csv(input_csv, output_csv, duplicate_log)
