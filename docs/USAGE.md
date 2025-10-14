# Usage Guide

## Basic Usage

### Quick Start

```bash
# Run a basic scan
python cloud_security_audit.py --provider aws

# This will:
# 1. Scan your AWS account
# 2. Generate security_audit_report.html
# 3. Display summary in terminal
```

## Command-Line Options

### Provider Selection

```bash
# Scan AWS (default)
python cloud_security_audit.py --provider aws

# Scan Azure (coming soon)
python cloud_security_audit.py --provider azure

# Scan GCP (coming soon)
python cloud_security_audit.py --provider gcp
```

### Region Selection

```bash
# Scan specific region
python cloud_security_audit.py --region us-east-1

# Australian region (default)
python cloud_security_audit.py --region ap-southeast-2

# European region
python cloud_security_audit.py --region eu-west-1
```

### Output Formats

```bash
# HTML report (default)
python cloud_security_audit.py --format html --output report.html

# JSON export (for automation)
python cloud_security_audit.py --format json --output findings.json

# CSV export (for spreadsheets)
python cloud_security_audit.py --format csv --output findings.csv

# All formats at once
python cloud_security_audit.py --format all --output security_audit
# Generates: security_audit.html, .json, .csv, _summary.txt, _summary.md
```

### Verbose and Quiet Modes

```bash
# Verbose output (includes executive summary)
python cloud_security_audit.py --verbose

# Quiet mode (minimal output)
python cloud_security_audit.py --quiet
```

## Automated Remediation

### Dry-Run Mode (Safe Testing)

```bash
# Test remediation without making changes
python cloud_security_audit.py --remediate --dry-run

# Output shows what WOULD be changed:
# [DRY RUN] Would enable encryption on bucket: my-bucket
# [DRY RUN] Would block public access on bucket: test-bucket
```

### Live Remediation

```bash
# Apply automatic fixes (requires confirmation)
python cloud_security_audit.py --remediate

# You will be prompted:
# [!] WARNING: Running in LIVE mode - changes will be applied!
# Are you sure you want to proceed? (yes/no):
```

**What Gets Remediated**:
- S3 encryption enabled
- S3 versioning enabled
- S3 public access blocked
- S3 logging enabled
- Security group rules restricted
- IMDSv2 enforced on EC2
- VPC Flow Logs enabled

**What Requires Manual Action**:
- IAM policy changes
- EBS encryption (requires downtime)
- CloudTrail configuration
- IAM user MFA setup

## Common Workflows

### Workflow 1: Initial Assessment

```bash
# 1. Run comprehensive scan
python cloud_security_audit.py --provider aws --format all --output initial_scan

# 2. Review HTML report
open reports/initial_scan_*.html

# 3. Review executive summary
cat reports/initial_scan_*_summary.txt

# 4. Export findings to CSV for tracking
# (CSV file already generated in reports/)
```

### Workflow 2: Test Remediation

```bash
# 1. Scan and see issues
python cloud_security_audit.py --output before_fix.html

# 2. Test fixes (dry-run)
python cloud_security_audit.py --remediate --dry-run

# 3. Review what would be changed
# Check terminal output for planned changes

# 4. Apply fixes
python cloud_security_audit.py --remediate

# 5. Re-scan to verify
python cloud_security_audit.py --output after_fix.html

# 6. Compare results
open before_fix.html
open after_fix.html
```

### Workflow 3: Scheduled Scanning

```bash
# Create scan script
cat > scan_daily.sh << 'EOF'
#!/bin/bash
cd /path/to/cloud-security-toolkit
source venv/bin/activate

DATE=$(date +%Y%m%d)
python cloud_security_audit.py \
  --provider aws \
  --format all \
  --output "daily_scan_$DATE" \
  --quiet

# Email report (optional)
# mail -s "Security Scan $DATE" admin@example.com < reports/daily_scan_${DATE}_summary.txt
EOF

chmod +x scan_daily.sh

# Add to crontab (daily at 2 AM)
# crontab -e
# 0 2 * * * /path/to/scan_daily.sh
```

### Workflow 4: Compliance Reporting

```bash
# Scan and generate compliance report
python cloud_security_audit.py \
  --provider aws \
  --format all \
  --output compliance_report_$(date +%Y%m%d) \
  --verbose

# Reports include:
# - CIS Benchmark mappings
# - ASD Essential Eight alignment
# - Compliance violation counts

# Review compliance violations in HTML report
```

## Understanding the Reports

### HTML Report Sections

1. **Header**: Scan date, account ID, region
2. **Security Score**: Overall score (0-100) with grade
3. **Statistics**: Count of CRITICAL/HIGH/MEDIUM/LOW findings
4. **Executive Summary**: Top risks and immediate actions
5. **Detailed Findings**: All issues with recommendations
6. **Compliance Violations**: Control mappings
7. **Findings by Type**: Resource breakdown

### JSON Report Structure

```json
{
  "metadata": {
    "scan_date": "2025-10-14T...",
    "total_findings": 42,
    "security_score": 67.5,
    "security_grade": "C+"
  },
  "summary": {
    "critical": 3,
    "high": 12,
    "medium": 20,
    "low": 7
  },
  "findings_by_type": { ... },
  "compliance_violations": { ... },
  "all_findings": [ ... ]
}
```

### CSV Report Columns

- `severity`: CRITICAL, HIGH, MEDIUM, LOW
- `resource`: Resource name/ID
- `type`: Resource type (S3 Bucket, IAM User, etc.)
- `issue`: Description of security issue
- `recommendation`: How to fix
- `risk_score`: Numeric risk score (0-100)
- `exposure`: public, internet-facing, internal
- `compliance`: Compliance control mappings

## Advanced Usage

### Filtering by Service

```bash
# Scan only specific services (coming soon)
python cloud_security_audit.py --services iam s3

# Scan everything except EC2
python cloud_security_audit.py --exclude ec2
```

### Custom Configuration

```bash
# Use custom config file
python cloud_security_audit.py --config my_custom_config.yaml

# Override specific settings
python cloud_security_audit.py --min-password-length 16
```

### Integration with CI/CD

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run security scan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          python cloud_security_audit.py \
            --format json \
            --output scan_results.json

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: security-scan-results
          path: scan_results.json

      - name: Check for critical findings
        run: |
          CRITICAL=$(jq '.summary.critical' scan_results.json)
          if [ "$CRITICAL" -gt 0 ]; then
            echo "CRITICAL findings detected!"
            exit 1
          fi
```

## Tips and Best Practices

### 1. Start with Dry-Run
Always test remediation in dry-run mode first:
```bash
python cloud_security_audit.py --remediate --dry-run
```

### 2. Regular Scanning
Set up daily or weekly scans to track security posture over time.

### 3. Review Before Remediation
Manually review findings before applying automated fixes:
```bash
# Generate report first
python cloud_security_audit.py --output review.html
open review.html
# Then remediate after review
```

### 4. Track Changes
Keep scan results over time to track improvements:
```bash
mkdir -p scan_history
python cloud_security_audit.py --output "scan_history/scan_$(date +%Y%m%d).html"
```

### 5. Export for Tracking
Use CSV exports to track remediation in project management tools:
```bash
python cloud_security_audit.py --format csv --output findings.csv
# Import into Jira, Trello, or Excel
```

### 6. Security Score Tracking
Track your security score over time:
```bash
python cloud_security_audit.py --format json --output scan.json
jq '.metadata.security_score' scan.json >> score_history.txt
```

## Troubleshooting

### Scan Takes Too Long
- Reduce scope to specific regions
- Scan fewer services
- Check network connectivity

### Permission Errors
- Verify IAM permissions (see INSTALLATION.md)
- Check CloudTrail for denied API calls

### No Findings Shown
- Verify credentials have correct permissions
- Check you're scanning the correct region
- Ensure resources exist in the account

## Getting Help

```bash
# Display help
python cloud_security_audit.py --help

# Check version
python cloud_security_audit.py --version

# For issues:
# - Check docs/ directory
# - Review troubleshooting guide
# - Open GitHub issue
```
