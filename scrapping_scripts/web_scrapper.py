import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import json
import time
import logging
from typing import Dict, Optional

class UnitRequirementsScraper:
    def __init__(self, 
                 input_csv_path: str = 'unit_search_results_full.csv',
                 output_csv_path: str = 'unit_search_results_full_updated.csv',
                 log_path: str = 'scraping_progress.log',
                 state_path: str = 'scraping_state.json'):
        """
        Initialize the scraper with necessary file paths and logging.
        
        Args:
            input_csv_path (str): Path to input CSV file
            output_csv_path (str): Path to output updated CSV file
            log_path (str): Path to logging file
            state_path (str): Path to store scraping state
        """
        # Configure logging
        logging.basicConfig(
            filename=log_path, 
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger()
        
        # File paths
        self.input_csv_path = input_csv_path
        self.output_csv_path = output_csv_path
        self.state_path = state_path
        
        # Scraping state
        self.state = self.load_state()
        
        # Requirement mappings
        self.requirement_types = {
            'Prerequisites': ['prerequisite', 'prerequisites'],
            'Corequisites': ['corequisite', 'corequisites'],
            'Prohibitions': ['prohibition', 'prohibitions'],
            'Assumed knowledge': ['assumed knowledge', 'assumed']
        }
        
        # Ensure output file exists with headers
        self.ensure_output_file_headers()
    
    def ensure_output_file_headers(self):
        """
        Ensure the output CSV file exists with headers.
        """
        if not os.path.exists(self.output_csv_path) or os.stat(self.output_csv_path).st_size == 0:
            with open(self.output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                headers = [
                    'Unit Code', 'Title', 'URL', 'Description', 
                    'Prerequisites', 'Corequisites', 'Prohibitions', 'Assumed Knowledge'
                ]
                writer.writerow(headers)

    
    def load_state(self) -> Dict:
        """
        Load scraping state from JSON file.
        
        Returns:
            Dict: Scraping state or default state
        """
        try:
            if os.path.exists(self.state_path):
                with open(self.state_path, 'r') as f:
                    return json.load(f)
            return {'last_processed_index': 0, 'failed_units': []}
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return {'last_processed_index': 0, 'failed_units': []}
    
    def save_state(self, last_index: int, failed_units: list):
        """
        Save current scraping state to JSON file.
        
        Args:
            last_index (int): Last processed unit index
            failed_units (list): List of units that failed scraping
        """
        state = {
            'last_processed_index': last_index,
            'failed_units': failed_units
        }
        try:
            with open(self.state_path, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
    
    def fetch_html_content(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL with robust error handling.
        
        Args:
            url (str): URL to fetch
        
        Returns:
            Optional[str]: HTML content or None
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def parse_unit_requirements(self, html_content: str) -> Dict:
        """
        Parse HTML to extract unit requirements.
        
        Args:
            html_content (str): HTML content to parse
        
        Returns:
            Dict: Parsed requirements
        """
        requirements = {req: 'None' for req in self.requirement_types.keys()}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tables = soup.find_all('table', class_=re.compile(r'table'))
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    header_cell = row.find('th')
                    content_cell = row.find('td')
                    
                    if header_cell and content_cell:
                        header_text = header_cell.get_text(strip=True, separator=' ').lower()
                        
                        for req_type, variations in self.requirement_types.items():
                            if any(variation in header_text for variation in variations):
                                content = content_cell.get_text(strip=True, separator=' ')
                                requirements[req_type] = content
        
        except Exception as e:
            self.logger.error(f"Error parsing requirements: {e}")
        
        return requirements
    
    def count_total_units(self) -> int:
        """
        Count total number of units in the input CSV.
        
        Returns:
            int: Total number of units
        """
        with open(self.input_csv_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            return sum(1 for _ in f)
    
    def process_units(self, batch_size: int = 1500):
        """
        Process units in batches with robust error handling and real-time reporting.
        
        Args:
            batch_size (int): Number of units to process in each batch
        """
        # Count total units
        total_units = self.count_total_units()
        
        failed_units = self.state.get('failed_units', [])
        start_index = self.state.get('last_processed_index', 0)
        
        print(f"\n--- Starting Unit Requirements Scraper ---")
        print(f"Total Units: {total_units}")
        print(f"Starting from Index: {start_index}")
        print(f"Batch Size: {batch_size}\n")
        
        with open(self.input_csv_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            # Skip headers and previously processed rows
            headers = next(reader)
            for _ in range(start_index):
                next(reader, None)
            
            processed_count = 0
            for row in reader:
                if processed_count >= batch_size:
                    break
                
                try:
                    unit_code, title, url, description = row[:4]
                    
                    # Print current processing status
                    print(f"Processing: {unit_code} ({start_index + processed_count + 1}/{total_units})")
                    
                    # Skip if URL is not valid
                    if not url or 'http' not in url:
                        print(f"  ⚠️ Skipping {unit_code}: Invalid URL\n")
                        continue
                    
                    html_content = self.fetch_html_content(url)
                    if not html_content:
                        print(f"  ❌ Failed to fetch {unit_code}\n")
                        failed_units.append(unit_code)
                        continue
                    
                    requirements = self.parse_unit_requirements(html_content)
                    
                    # Extend row with requirements
                    full_row = row + [
                        requirements['Prerequisites'],
                        requirements['Corequisites'],
                        requirements['Prohibitions'],
                        requirements['Assumed knowledge']
                    ]
                    
                    # Append to output file immediately
                    with open(self.output_csv_path, 'a', newline='', encoding='utf-8') as outfile:
                        writer = csv.writer(outfile)
                        writer.writerow(full_row)
                    
                    print(f"  ✅ Processed {unit_code} successfully\n")
                    processed_count += 1
                    
                    # Add random delay to be respectful of server
                    time.sleep(0.1)
                
                except Exception as e:
                    print(f"  ❌ Error processing {unit_code}: {e}\n")
                    self.logger.error(f"Error processing {unit_code}: {e}")
                    failed_units.append(unit_code)
            
            # Update and save state
            self.save_state(start_index + processed_count, failed_units)
            
            # Final summary
            print("\n--- Scraping Batch Complete ---")
            print(f"Processed Units: {processed_count}")
            print(f"Failed Units: {len(failed_units)}")
            print(f"Failed Units List: {failed_units}")
            
            self.logger.info(f"Processed {processed_count} units. Failed units: {len(failed_units)}")

def main():
    scraper = UnitRequirementsScraper()
    scraper.process_units()

if __name__ == "__main__":
    main()