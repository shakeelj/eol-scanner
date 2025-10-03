#!/usr/bin/env python3
"""
End of Life Scanner
Scans software packages from CSV against endoflife.date API to check EOL status.
"""

import csv
import json
import os
import sys
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EOLScanner:
    """Main class for scanning software packages against endoflife.date API."""
    
    def __init__(self, api_base_url: str = "https://endoflife.date/api"):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EOL-Scanner/1.0'
        })
        
    def get_all_products(self) -> Dict[str, any]:
        """Fetch all products from endoflife.date API."""
        try:
            response = self.session.get(f"{self.api_base_url}/all.json", timeout=30)
            response.raise_for_status()
            data = response.json()
            # Handle both dict and list responses
            if isinstance(data, list):
                return {item: {} for item in data}
            return data
        except requests.Timeout:
            logger.error("API request timed out")
            return {}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch products from API: {e}")
            return {}
    
    def get_product_cycles(self, product: str) -> List[Dict]:
        """Get lifecycle information for a specific product."""
        try:
            response = self.session.get(f"{self.api_base_url}/{product}.json", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.warning(f"API request timed out for {product}")
            return []
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch cycles for {product}: {e}")
            return []
    
    def find_product_match(self, package_name: str, all_products: Dict) -> Optional[str]:
        """Find the best matching product in the endoflife.date database."""
        package_lower = package_name.lower()
        
        # Direct match
        if package_lower in all_products:
            return package_lower
        
        # Try to find partial matches
        for product in all_products.keys():
            if package_lower in product or product in package_lower:
                return product
        
        # Try to find matches with common variations
        variations = [
            package_lower.replace('-', ''),
            package_lower.replace('_', ''),
            package_lower.replace('.', ''),
            package_lower.split()[0] if ' ' in package_lower else package_lower
        ]
        
        for variation in variations:
            if variation in all_products:
                return variation
            for product in all_products.keys():
                if variation in product or product in variation:
                    return product
        
        return None
    
    def check_eol_status(self, product: str, version: str = None) -> Dict:
        """Check EOL status for a product and version."""
        cycles = self.get_product_cycles(product)
        if not cycles:
            return {
                'product': product,
                'version': version,
                'status': 'unknown',
                'eol_date': None,
                'support_status': 'unknown',
                'message': 'Product not found in EOL database'
            }
        
        # If no version specified, return general product info
        if not version:
            latest_cycle = cycles[0] if cycles else None
            return {
                'product': product,
                'version': 'latest',
                'status': 'found',
                'eol_date': latest_cycle.get('eol') if latest_cycle else None,
                'support_status': 'active' if not latest_cycle.get('eol') else 'eol',
                'message': f'Found {len(cycles)} versions'
            }
        
        # Find specific version
        for cycle in cycles:
            if cycle.get('cycle') == version:
                eol_date = cycle.get('eol')
                is_eol = eol_date is not None
                return {
                    'product': product,
                    'version': version,
                    'status': 'found',
                    'eol_date': eol_date,
                    'support_status': 'eol' if is_eol else 'active',
                    'message': f'EOL date: {eol_date}' if is_eol else 'Still supported'
                }
        
        # Version not found, return closest match
        return {
            'product': product,
            'version': version,
            'status': 'version_not_found',
            'eol_date': None,
            'support_status': 'unknown',
            'message': f'Version {version} not found for {product}'
        }
    
    def process_csv(self, csv_file: str, output_dir: str) -> None:
        """Process CSV file and generate EOL reports."""
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            return
        
        if not csv_file.lower().endswith('.csv'):
            logger.error(f"File is not a CSV file: {csv_file}")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Fetch all products from API
        logger.info("Fetching product list from endoflife.date API...")
        all_products = self.get_all_products()
        logger.info(f"Found {len(all_products)} products in EOL database")
        
        # Process CSV file
        results = []
        matched_products = set()
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Try to detect CSV format
                sample = file.read(1024)
                file.seek(0)
                
                # Common CSV formats for JFrog exports
                possible_delimiters = [',', ';', '\t']
                delimiter = ','
                
                for delim in possible_delimiters:
                    if delim in sample:
                        delimiter = delim
                        break
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    # Try to extract package name and version from common JFrog CSV columns
                    package_name = None
                    version = None
                
                    # Common column names in JFrog exports
                    name_columns = ['name', 'package_name', 'package', 'component', 'artifact']
                    version_columns = ['version', 'package_version', 'ver', 'release']
                    
                    for col in name_columns:
                        if col in row and row[col]:
                            package_name = row[col].strip()
                            break
                    
                    for col in version_columns:
                        if col in row and row[col]:
                            version = row[col].strip()
                            break
                    
                    if not package_name:
                        logger.warning(f"Row {row_num}: No package name found")
                        continue
                
                    # Find matching product
                    matched_product = self.find_product_match(package_name, all_products)
                    
                    if matched_product:
                        matched_products.add(matched_product)
                        eol_status = self.check_eol_status(matched_product, version)
                        eol_status['original_package'] = package_name
                        eol_status['row_number'] = row_num
                        eol_status['raw_data'] = row
                    else:
                        eol_status = {
                            'product': package_name,
                            'version': version,
                            'status': 'not_found',
                            'eol_date': None,
                            'support_status': 'unknown',
                            'message': 'Package not found in EOL database',
                            'original_package': package_name,
                            'row_number': row_num,
                            'raw_data': row
                        }
                    
                    results.append(eol_status)
                    logger.info(f"Processed {package_name} (row {row_num})")
                    
        except UnicodeDecodeError:
            logger.error(f"CSV file encoding error. Try saving as UTF-8: {csv_file}")
            return
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return
        
        # Generate reports
        self.generate_reports(results, output_dir, matched_products)
        
        logger.info(f"Processing complete. Results saved to {output_dir}")
    
    def generate_reports(self, results: List[Dict], output_dir: str, matched_products: set) -> None:
        """Generate various report formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Summary report
        summary = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_packages': len(results),
            'matched_products': len(matched_products),
            'eol_packages': len([r for r in results if r.get('support_status') == 'eol']),
            'active_packages': len([r for r in results if r.get('support_status') == 'active']),
            'unknown_packages': len([r for r in results if r.get('support_status') == 'unknown']),
            'not_found_packages': len([r for r in results if r.get('status') == 'not_found'])
        }
        
        # Save summary
        with open(os.path.join(output_dir, f'summary_{timestamp}.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save detailed results
        with open(os.path.join(output_dir, f'detailed_results_{timestamp}.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate CSV report
        csv_file = os.path.join(output_dir, f'eol_report_{timestamp}.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        # Generate EOL-only report
        eol_packages = [r for r in results if r.get('support_status') == 'eol']
        if eol_packages:
            eol_file = os.path.join(output_dir, f'eol_packages_{timestamp}.csv')
            with open(eol_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=eol_packages[0].keys())
                writer.writeheader()
                writer.writerows(eol_packages)
        
        # Generate HTML report
        self.generate_html_report(results, output_dir, timestamp, summary)
        
        logger.info(f"Generated reports:")
        logger.info(f"  - Summary: summary_{timestamp}.json")
        logger.info(f"  - Detailed: detailed_results_{timestamp}.json")
        logger.info(f"  - CSV: eol_report_{timestamp}.csv")
        if eol_packages:
            logger.info(f"  - EOL only: eol_packages_{timestamp}.csv")
        logger.info(f"  - HTML: eol_report_{timestamp}.html")
    
    def generate_html_report(self, results: List[Dict], output_dir: str, timestamp: str, summary: Dict) -> None:
        """Generate HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EOL Scan Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .eol {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
        .active {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
        .unknown {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
        .not-found {{ background-color: #f3e5f5; border-left: 4px solid #9c27b0; }}
        .package {{ margin: 10px 0; padding: 10px; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>End of Life Scan Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Scan Date:</strong> {summary['scan_timestamp']}</p>
        <p><strong>Total Packages:</strong> {summary['total_packages']}</p>
        <p><strong>Matched Products:</strong> {summary['matched_products']}</p>
        <p><strong>EOL Packages:</strong> {summary['eol_packages']}</p>
        <p><strong>Active Packages:</strong> {summary['active_packages']}</p>
        <p><strong>Unknown Status:</strong> {summary['unknown_packages']}</p>
        <p><strong>Not Found:</strong> {summary['not_found_packages']}</p>
    </div>
    
    <h2>Package Details</h2>
    <table>
        <tr>
            <th>Package</th>
            <th>Version</th>
            <th>Status</th>
            <th>EOL Date</th>
            <th>Message</th>
        </tr>
"""
        
        for result in results:
            status_class = result.get('support_status', 'unknown')
            html_content += f"""
        <tr class="{status_class}">
            <td>{result.get('product', 'N/A')}</td>
            <td>{result.get('version', 'N/A')}</td>
            <td>{result.get('support_status', 'unknown')}</td>
            <td>{result.get('eol_date', 'N/A')}</td>
            <td>{result.get('message', 'N/A')}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(os.path.join(output_dir, f'eol_report_{timestamp}.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Scan software packages for EOL status')
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file containing package information (optional if using input folder)')
    parser.add_argument('-o', '--output', default='output', help='Output directory for results')
    parser.add_argument('-i', '--input', default='input', help='Input directory containing CSV files')
    parser.add_argument('--api-url', default='https://endoflife.date/api', help='API base URL')
    parser.add_argument('--scan-all', action='store_true', help='Scan all CSV files in input directory')
    
    args = parser.parse_args()
    
    scanner = EOLScanner(args.api_url)
    
    # If no specific CSV file provided, scan input directory
    if not args.csv_file:
        if args.scan_all:
            # Scan all CSV files in input directory
            input_dir = Path(args.input)
            if not input_dir.exists():
                logger.error(f"Input directory not found: {input_dir}")
                return
            
            csv_files = list(input_dir.glob("*.csv"))
            if not csv_files:
                logger.error(f"No CSV files found in {input_dir}")
                return
            
            logger.info(f"Found {len(csv_files)} CSV files to process")
            for csv_file in csv_files:
                logger.info(f"Processing {csv_file.name}...")
                output_subdir = Path(args.output) / csv_file.stem
                scanner.process_csv(str(csv_file), str(output_subdir))
        else:
            # Look for a single CSV file in input directory
            input_dir = Path(args.input)
            if not input_dir.exists():
                logger.error(f"Input directory not found: {input_dir}")
                return
            
            csv_files = list(input_dir.glob("*.csv"))
            if not csv_files:
                logger.error(f"No CSV files found in {input_dir}")
                logger.info("Please place your CSV file in the 'input' directory")
                return
            
            if len(csv_files) > 1:
                logger.warning(f"Multiple CSV files found in {input_dir}. Using {csv_files[0].name}")
                logger.info("Use --scan-all to process all CSV files")
            
            scanner.process_csv(str(csv_files[0]), args.output)
    else:
        # Process specific CSV file
        scanner.process_csv(args.csv_file, args.output)

if __name__ == '__main__':
    main()
