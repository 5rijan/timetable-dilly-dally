import csv
import json

def compare_csv_files(original_file, new_file, log_file):
    # Read Unit Codes from the original CSV file
    with open(original_file, 'r', encoding='utf-8') as csvfile:
        original_reader = csv.DictReader(csvfile)
        original_unit_codes = set()
        for row in original_reader:
            if 'Unit Code' in row and row['Unit Code']:  # Check if 'Unit Code' exists and is not empty
                original_unit_codes.add(row['Unit Code'])
        print(f"Original CSV row count: {len(original_unit_codes)}")

    # Read Unit Codes from the new CSV file
    with open(new_file, 'r', encoding='utf-8') as csvfile:
        new_reader = csv.DictReader(csvfile)
        new_unit_codes = set()
        for row in new_reader:
            if 'Unit Code' in row and row['Unit Code']:  # Check if 'Unit Code' exists and is not empty
                new_unit_codes.add(row['Unit Code'])
        print(f"New CSV row count: {len(new_unit_codes)}")

    # Find missing Unit Codes in both files
    missing_in_new = list(original_unit_codes - new_unit_codes)
    missing_in_original = list(new_unit_codes - original_unit_codes)

    # Log missing Unit Codes to a JSON file
    with open(log_file, 'w', encoding='utf-8') as jsonfile:
        json.dump({
            "missing_in_new": missing_in_new,
            "missing_in_original": missing_in_original
        }, jsonfile, indent=4)

    print(f"Comparison complete. Missing Unit Codes logged in '{log_file}'.")

if __name__ == "__main__":
    original_csv = "uos.csv"  # Replace with your original CSV file path
    new_csv = "final.csv"  # Replace with your new CSV file path
    log_file = "missing_units.json"  # Replace with your desired log file path

    compare_csv_files(original_csv, new_csv, log_file)
