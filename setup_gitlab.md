# GitLab Setup Guide

This guide will walk you through setting up the EOL Scanner project in GitLab with CI/CD pipelines.

## Prerequisites

- GitLab account with repository creation permissions
- Basic knowledge of Git and GitLab CI/CD

## Step-by-Step Setup

### 1. Create a New GitLab Project

1. Log into your GitLab account
2. Click **"New project"** → **"Create blank project"**
3. Fill in the project details:
   - **Project name**: `eol-scanner`
   - **Project slug**: `eol-scanner` (or your preferred name)
   - **Visibility level**: Choose based on your needs
   - **Initialize repository**: ✅ Check this box
4. Click **"Create project"**

### 2. Upload Project Files

#### Option A: Using Git (Recommended)

```bash
# Clone your new repository
git clone https://gitlab.com/your-username/eol-scanner.git
cd eol-scanner

# Copy all project files to this directory
# (Copy eol_scanner.py, requirements.txt, .gitlab-ci.yml, README.md, etc.)

# Add and commit files
git add .
git commit -m "Initial commit: EOL Scanner project"
git push origin main
```

#### Option B: Using GitLab Web Interface

1. Go to your project's **Repository** → **Files**
2. Click **"Upload file"** and upload each file:
   - `eol_scanner.py`
   - `requirements.txt`
   - `.gitlab-ci.yml`
   - `README.md`
   - `example_packages.csv`

### 3. Upload Your CSV File

1. Go to **Repository** → **Files**
2. Click **"Upload file"**
3. Upload your JFrog export CSV file
4. Name it `packages.csv` (or update the `CSV_FILE` variable in `.gitlab-ci.yml`)

### 4. Configure CI/CD Variables (Optional)

1. Go to **Settings** → **CI/CD** → **Variables**
2. Add any custom variables:
   - `CSV_FILE`: Name of your CSV file (default: `packages.csv`)
   - `OUTPUT_DIR`: Output directory name (default: `eol_results`)
   - `PYTHON_VERSION`: Python version (default: `3.9`)

### 5. Run Your First Pipeline

#### Automatic Trigger
1. Push any changes to the `main` branch
2. Go to **CI/CD** → **Pipelines**
3. Watch the pipeline execute

#### Manual Trigger
1. Go to **CI/CD** → **Pipelines**
2. Click **"Run pipeline"**
3. Select the branch (usually `main`)
4. Click **"Run pipeline"**

### 6. Set Up Scheduled Scans (Optional)

1. Go to **CI/CD** → **Schedules**
2. Click **"New schedule"**
3. Configure the schedule:
   - **Description**: `Daily EOL Scan`
   - **Interval pattern**: `0 2 * * *` (daily at 2 AM UTC)
   - **Target branch**: `main`
   - **Variables**: Leave empty (uses defaults)
4. Click **"Save"**

## Pipeline Jobs Explained

### 1. `setup` Job
- **Purpose**: Prepares the Python environment
- **Triggers**: Every pipeline run
- **Duration**: ~1-2 minutes

### 2. `eol_scan` Job
- **Purpose**: Runs the EOL scanner automatically
- **Triggers**: 
  - Push to `main` or `develop` branches
  - Merge requests
  - Scheduled runs
- **Duration**: Depends on CSV size (typically 2-10 minutes)

### 3. `manual_scan` Job
- **Purpose**: Manual trigger for custom scans
- **Triggers**: Manual only
- **Usage**: Click "Run" button in GitLab UI

### 4. `scheduled_scan` Job
- **Purpose**: Automated daily scans
- **Triggers**: Scheduled runs only
- **Fallback**: Creates example CSV if none provided

## Accessing Results

### 1. Download Artifacts
1. Go to **CI/CD** → **Pipelines**
2. Click on a completed pipeline
3. In the **Jobs** section, find the `eol_scan` job
4. Click **"Download"** next to the artifacts

### 2. View Results in GitLab
1. Go to **CI/CD** → **Pipelines**
2. Click on a completed pipeline
3. Click on the `eol_scan` job
4. Scroll down to the **Artifacts** section
5. Click on individual files to view them

## Customizing the Pipeline

### Environment Variables

Add these in **Settings** → **CI/CD** → **Variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `CSV_FILE` | `packages.csv` | Name of your CSV file |
| `OUTPUT_DIR` | `eol_results` | Output directory name |
| `PYTHON_VERSION` | `3.9` | Python version to use |

### Custom Schedule Patterns

Common cron patterns for scheduled scans:

| Pattern | Description |
|---------|-------------|
| `0 2 * * *` | Daily at 2 AM UTC |
| `0 2 * * 1` | Weekly on Monday at 2 AM UTC |
| `0 2 1 * *` | Monthly on the 1st at 2 AM UTC |
| `0 */6 * * *` | Every 6 hours |

### Pipeline Modifications

To modify the pipeline behavior, edit `.gitlab-ci.yml`:

```yaml
# Add custom stages
stages:
  - setup
  - scan
  - notify
  - artifacts

# Add notification job
notify:
  stage: notify
  script:
    - echo "Scan completed! Check artifacts for results."
  when: on_success
```

## Troubleshooting

### Common Issues

1. **Pipeline fails with "CSV file not found"**
   - Ensure your CSV file is named `packages.csv` (or update `CSV_FILE` variable)
   - Check that the file is in the repository root

2. **Scanner times out**
   - Large CSV files may take longer to process
   - Consider splitting large files into smaller batches

3. **No packages matched**
   - Verify package names in your CSV match those in endoflife.date
   - Check the scanner logs for matching details

4. **API rate limiting**
   - The scanner includes built-in rate limiting
   - For very large datasets, consider running in smaller batches

### Debug Mode

To enable debug logging, modify the pipeline:

```yaml
eol_scan:
  # ... existing configuration ...
  script:
    - python eol_scanner.py ${CSV_FILE} -o ${OUTPUT_DIR} --debug
```

### Viewing Logs

1. Go to **CI/CD** → **Pipelines**
2. Click on a pipeline run
3. Click on the job name (e.g., `eol_scan`)
4. Scroll through the job logs to see detailed output

## Security Considerations

- **CSV Data**: Ensure your CSV files don't contain sensitive information
- **API Access**: The scanner only reads from the public endoflife.date API
- **Artifacts**: Results are stored as GitLab artifacts (check retention policies)

## Best Practices

1. **Regular Updates**: Keep your CSV files updated with current package versions
2. **Scheduled Scans**: Set up regular scheduled scans for continuous monitoring
3. **Result Review**: Regularly review EOL reports and plan upgrades accordingly
4. **Backup**: Keep copies of important scan results outside of GitLab

## Support

If you encounter issues:

1. Check the pipeline logs for error messages
2. Verify your CSV file format matches the expected structure
3. Test the scanner locally first using the test script
4. Review the endoflife.date API documentation for supported products
