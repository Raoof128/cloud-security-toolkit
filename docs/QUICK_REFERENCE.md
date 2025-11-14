# Quick Reference Guide

Fast reference for common commands and workflows.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Tips & Tricks](#tips--tricks)

---

## Installation

```bash
# Clone repository
git clone https://github.com/Raoof128/cloud-security-toolkit.git
cd cloud-security-toolkit

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install .

# Or with development tools
pip install -e ".[dev]"
```

---

## Basic Usage

### Demo Mode (No AWS Required)

```bash
python cloud_security_audit.py --demo
python cloud_security_audit.py --demo --output demo_report.html
python cloud_security_audit.py --demo --format all
```

### AWS Scanning

```bash
# Configure AWS credentials first
aws configure

# Basic scan
python cloud_security_audit.py --provider aws

# Scan with HTML report
python cloud_security_audit.py --provider aws --output report.html

# Scan specific region
python cloud_security_audit.py --provider aws --region us-east-1

# All report formats
python cloud_security_audit.py --provider aws --format all --output scan
```

### Remediation

```bash
# Dry-run mode (safe, no changes)
python cloud_security_audit.py --provider aws --remediate --dry-run

# Live mode (makes actual changes - requires confirmation)
python cloud_security_audit.py --provider aws --remediate
```

---

## Common Commands

### Using Makefile

```bash
make help              # Show all available commands
make test              # Run test suite
make test-cov          # Run tests with coverage
make lint              # Check code quality
make format            # Auto-format code with black
make security          # Run security checks
make demo              # Run demo mode
make verify            # Verify installation
make clean             # Clean generated files
```

### Using Docker

```bash
# Build image
docker build -t cloud-security-toolkit .

# Run demo
docker run --rm cloud-security-toolkit --demo

# Run AWS scan
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit \
  --provider aws --output /app/reports/scan.html

# Using docker-compose
docker-compose up scanner
```

### Programmatic Usage

```python
from scanners.aws_scanner import AWSSecurityScanner
from utils.risk_scoring import RiskScorer
from reporting.report_generator import SecurityReportGenerator

# Scan
scanner = AWSSecurityScanner(region='us-east-1')
findings = scanner.run_full_scan()

# Score
scorer = RiskScorer()
prioritized = scorer.prioritize_findings(findings)
stats = scorer.generate_summary_stats(prioritized)

# Report
reporter = SecurityReportGenerator()
reporter.generate_html_report(prioritized, stats, 'report.html')
```

---

## Troubleshooting

### No AWS Credentials

```bash
# Check credentials
aws sts get-caller-identity

# Configure credentials
aws configure

# Check env vars
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### Permission Denied

```bash
# Check IAM permissions
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# Test with AWS CLI
aws s3 ls
aws iam list-users
```

### Module Not Found

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+

# Check boto3 installation
python -c "import boto3; print(boto3.__version__)"
```

### Reports Not Generated

```bash
# Check output directory
ls -la reports/

# Create reports directory
mkdir -p reports

# Check permissions
chmod 755 reports

# Run with verbose output
python cloud_security_audit.py --provider aws --verbose
```

---

## Tips & Tricks

### Save Time with Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias cst='python /path/to/cloud_security_audit.py'
alias cst-demo='python /path/to/cloud_security_audit.py --demo'
alias cst-aws='python /path/to/cloud_security_audit.py --provider aws'
```

### Scheduled Scans

```bash
# Add to crontab
crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/cloud-security-toolkit && python cloud_security_audit.py --provider aws --output reports/daily_$(date +\%Y\%m\%d).html
```

### Filter Findings

```bash
# Show only critical findings
python cloud_security_audit.py --provider aws --format json | jq '.findings[] | select(.severity=="CRITICAL")'

# Count by severity
python cloud_security_audit.py --provider aws --format json | jq '.findings | group_by(.severity) | map({severity: .[0].severity, count: length})'
```

### Multi-Account Scanning

```bash
# Loop through AWS profiles
for profile in prod staging dev; do
  AWS_PROFILE=$profile python cloud_security_audit.py \
    --provider aws \
    --output reports/${profile}_scan.html
done
```

### Compare Scans

```bash
# Run baseline scan
python cloud_security_audit.py --provider aws --format json --output baseline.json

# Run follow-up scan
python cloud_security_audit.py --provider aws --format json --output current.json

# Compare
diff <(jq -S . baseline.json) <(jq -S . current.json)
```

### Export for Tracking

```bash
# Export to CSV for tracking in spreadsheets
python cloud_security_audit.py --provider aws --format csv --output findings.csv

# Import into Excel, Google Sheets, etc.
```

### Custom Filtering

```python
# Filter critical S3 findings only
findings = scanner.run_full_scan()
critical_s3 = [
    f for f in findings
    if f['severity'] == 'CRITICAL' and f['type'] == 'S3 Bucket'
]
```

### Quick Security Score

```bash
# Get just the security score
python cloud_security_audit.py --provider aws --format json | jq '.metadata.security_score'
```

### Remediation Workflow

```bash
# 1. Test in dry-run
python cloud_security_audit.py --provider aws --remediate --dry-run

# 2. Review logs
cat remediation_log.json

# 3. Apply if safe
python cloud_security_audit.py --provider aws --remediate

# 4. Verify changes
python cloud_security_audit.py --provider aws
```

---

## Keyboard Shortcuts (CLI)

When running interactively:

- `Ctrl+C` - Stop current scan
- `Ctrl+Z` - Suspend process (resume with `fg`)
- `Ctrl+D` - Exit Python REPL

---

## Environment Variables

```bash
# AWS Configuration
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=production

# Application Configuration
export PYTHONUNBUFFERED=1      # Real-time output
export LOG_LEVEL=DEBUG         # Verbose logging
```

---

## File Locations

```
~/.aws/credentials           # AWS credentials
~/.aws/config                # AWS config
./config/aws_config.yaml     # Tool configuration
./reports/                   # Generated reports
./remediation_log*.json      # Remediation audit logs
```

---

## Exit Codes

```
0   - Success
1   - General error
2   - No findings
126 - Permission denied
127 - Command not found
130 - Interrupted (Ctrl+C)
```

---

## Quick Checks

```bash
# Check installation
python verify_installation.py

# Test AWS connectivity
aws sts get-caller-identity

# Check Python version
python --version

# List available regions
aws ec2 describe-regions --query 'Regions[].RegionName' --output text

# Check current IAM identity
aws iam get-user
```

---

## Performance

```bash
# Scan single service (faster)
# (requires code modification or feature implementation)

# Scan specific region only
python cloud_security_audit.py --provider aws --region us-east-1

# Use demo mode for testing (instant)
python cloud_security_audit.py --demo
```

---

## Getting Help

```bash
# Command help
python cloud_security_audit.py --help

# Python module help
python -c "from scanners.aws_scanner import AWSSecurityScanner; help(AWSSecurityScanner)"

# Online documentation
# https://github.com/Raoof128/cloud-security-toolkit/tree/main/docs
```

---

## Useful Links

- **Repository**: https://github.com/Raoof128/cloud-security-toolkit
- **Issues**: https://github.com/Raoof128/cloud-security-toolkit/issues
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Security**: [SECURITY.md](../SECURITY.md)
- **API Docs**: [API.md](API.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Last Updated**: 2025-11-14
**Version**: 2.0.0
