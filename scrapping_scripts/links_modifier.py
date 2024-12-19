import json
import re
from pathlib import Path

def extract_unit_codes(text):
    if not text or text.lower() == "none":
        return []
    return re.findall(r"\b[A-Z]{4}\d{4}\b", text)

def fix_links_and_nodes(data):
    """Ensures all nodes in links are present in the nodes array."""
    node_ids = {node["id"] for node in data["nodes"]}
    missing_nodes = set()

    # Fix links
    for link in data["links"]:
        if link["source"] not in node_ids:
            missing_nodes.add(link["source"])
        if link["target"] not in node_ids:
            missing_nodes.add(link["target"])

    # Add placeholder nodes for missing nodes
    for missing in missing_nodes:
        data["nodes"].append({
            "id": missing,
            "title": f"Placeholder for {missing}",
            "url": "",
            "description": "Auto-generated placeholder node."
        })

    return data

def process_and_fix_json(input_json, output_json):
    # Read the input JSON
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Fix nodes and links
    fixed_data = fix_links_and_nodes(data)

    # Write the fixed JSON back to output
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(fixed_data, f, indent=4)

    print(f"Fixed JSON saved to: {output_json}")


input_json_file = "data/json/prohibition_uos.json"
output_json_file = "fixed_corequisites_uos.json"
process_and_fix_json(input_json_file, output_json_file)
