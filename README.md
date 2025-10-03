# End of Life (EOL) Scanner

A Python-based tool that scans software packages from CSV files against the [endoflife.date](https://endoflife.date/) API to check for end-of-life status. This project is designed to run in GitLab CI/CD pipelines and provides comprehensive reporting.

## Features

- 📊 **CSV Processing**: Automatically detects and processes JFrog export CSV files
- 🔍 **Smart Matching**: Intelligent package name matching against the endoflife.date database
- 📈 **Multiple Report Formats**: JSON, CSV, and HTML reports
- 🚀 **GitLab CI/CD Integration**: Ready-to-use pipeline configuration
- 📋 **Comprehensive Analysis**: EOL status, support lifecycle, and detailed reporting

## Project Structure

```
├── eol_scanner.py          # Main Python script
├── requirements.txt         # Python dependencies
├── .gitlab-ci.yml          # GitLab CI/CD pipeline
├── README.md               # This file
├── example_packages.csv    # Example CSV file
└── eol_results/           # Output directory (created during execution)
```

## Quick Start

### 1. Local Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run scanner with your CSV file
python eol_scanner.py your_packages.csv -o results

# View results
ls results/
```

### 2. GitLab CI/CD Setup

1. **Create a new GitLab project** and push this code
2. **Upload your CSV file** to the repository root (name it `packages.csv`)
3. **Run the pipeline** manually or set up scheduled runs

## CSV File Format

The scanner supports various CSV formats commonly exported from JFrog. It automatically detects the following column names:

**Package Name Columns:**
- `name`, `package_name`, `package`, `component`, `artifact`

**Version Columns:**
- `version`, `package_version`, `ver`, `release`

### Example CSV Format

```csv
package_name,version
python,3.8
nodejs,14.21.3
java,8
nginx,1.18.0
```

## GitLab CI/CD Configuration

### Pipeline Stages

1. **Setup**: Installs Python dependencies
2. **Scan**: Runs the EOL scanner
3. **Artifacts**: Provides download links for results

### Pipeline Jobs

- **`eol_scan`**: Automatic scan when code is pushed
- **`manual_scan`**: Manual trigger for custom scans
- **`scheduled_scan`**: Daily scheduled scans (2 AM UTC)

### Setting Up Scheduled Scans

1. Go to **CI/CD > Schedules** in your GitLab project
2. Click **New schedule**
3. Set **Interval pattern**: `0 2 * * *` (daily at 2 AM UTC)
4. Choose **Target branch**: `main`
5. Save the schedule

## Output Reports

The scanner generates multiple report formats:

### 1. Summary Report (`summary_YYYYMMDD_HHMMSS.json`)
```json
{
  "scan_timestamp": "2024-01-15T10:30:00",
  "total_packages": 150,
  "matched_products": 120,
  "eol_packages": 15,
  "active_packages": 95,
  "unknown_packages": 10,
  "not_found_packages": 30
}
```

### 2. Detailed Results (`detailed_results_YYYYMMDD_HHMMSS.json`)
Complete scan results with package details, EOL dates, and status.

### 3. CSV Report (`eol_report_YYYYMMDD_HHMMSS.csv`)
Spreadsheet-friendly format for further analysis.

### 4. EOL-Only Report (`eol_packages_YYYYMMDD_HHMMSS.csv`)
Contains only packages that have reached end-of-life.

### 5. HTML Report (`eol_report_YYYYMMDD_HHMMSS.html`)
Visual report with color-coded status indicators.

## Usage Examples

### Command Line Options

```bash
# Basic usage
python eol_scanner.py packages.csv

# Custom output directory
python eol_scanner.py packages.csv -o custom_results

# Custom API URL (if using a mirror)
python eol_scanner.py packages.csv --api-url https://your-mirror.com/api
```

### GitLab Variables

You can customize the pipeline using GitLab CI/CD variables:

- `CSV_FILE`: Name of your CSV file (default: `packages.csv`)
- `OUTPUT_DIR`: Output directory name (default: `eol_results`)
- `PYTHON_VERSION`: Python version to use (default: `3.9`)

## API Integration

The scanner integrates with the [endoflife.date API](https://endoflife.date/api):

- **All Products**: `GET /api/all.json`
- **Product Cycles**: `GET /api/{product}.json`

### Supported Products

The scanner can check EOL status for 400+ products including:
- Programming languages (Python, Java, Node.js, PHP, etc.)
- Frameworks (Angular, Django, React, etc.)
- Databases (MongoDB, PostgreSQL, MySQL, etc.)
- Operating systems (Windows, Linux distributions, etc.)
- And many more...

## Troubleshooting

### Common Issues

1. **CSV file not found**
   - Ensure your CSV file is in the repository root
   - Check the filename matches the `CSV_FILE` variable

2. **No packages matched**
   - Verify package names in your CSV
   - Check the endoflife.date database for exact product names

3. **API rate limiting**
   - The scanner includes rate limiting and retry logic
   - For large datasets, consider running in smaller batches

### Debug Mode

Enable detailed logging by modifying the script:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Check the [endoflife.date documentation](https://endoflife.date/)
- Review GitLab CI/CD logs for debugging
- Open an issue in this repository
