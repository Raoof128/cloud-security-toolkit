# Quick Start Guide

Get started with the Cloud Security Audit & Hardening Toolkit in 5 minutes!

## Prerequisites

- Python 3.10+
- AWS account with credentials
- 5-10 minutes

## Step 1: Installation (2 minutes)

```bash
# Clone repository
git clone https://github.com/raoufchak/cloud-security-toolkit.git
cd cloud-security-toolkit

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure AWS (1 minute)

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: ap-southeast-2 (or your preferred region)
# Default output format: json

# Verify credentials
aws sts get-caller-identity
```

## Step 3: Run Your First Scan (2 minutes)

```bash
# Run scan
python cloud_security_audit.py --provider aws --output my_first_scan.html

# Wait for scan to complete (usually 1-3 minutes)
# You'll see progress messages like:
#   [*] Starting AWS security scan...
#   [*] Scanning IAM users...
#   [*] Scanning S3 buckets...
#   ...
```

## Step 4: Review Results (1 minute)

```bash
# Open HTML report
open my_first_scan.html  # macOS
xdg-open my_first_scan.html  # Linux
start my_first_scan.html  # Windows
```

The report shows:
- **Security Score**: 0-100 rating with grade
- **Findings Summary**: Count of CRITICAL/HIGH/MEDIUM/LOW issues
- **Top Risks**: Most important security issues to address
- **Detailed Findings**: All issues with remediation steps

## Step 5: Test Remediation (Optional)

```bash
# Test automatic fixes (no changes made)
python cloud_security_audit.py --remediate --dry-run

# Review what would be fixed in the terminal output
```

## Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║  Cloud Security Audit & Hardening Toolkit                    ║
╚═══════════════════════════════════════════════════════════════╝

[*] Starting AWS security scan...
[*] Account: 123456789012
[*] Region: ap-southeast-2

[*] Scanning IAM configuration...
  [*] Checking IAM users...
  [+] Found 3 IAM-related issues

[*] Scanning S3 buckets...
  [*] Found 5 buckets to scan
  [+] Found 8 S3-related issues

[*] Scanning network security...
  [*] Found 12 security groups
  [+] Found 4 security group issues

[+] Scan complete!
[+] Total findings: 15

================================================================================
SCAN RESULTS SUMMARY
================================================================================
Security Score: 72.5/100 (Grade: B-)
Total Findings: 15
  Critical: 2
  High:     5
  Medium:   6
  Low:      2

Immediate Action Required: 7 findings
================================================================================

[+] HTML report generated: my_first_scan.html
```

## What's Next?

### Fix Critical Issues

Open the HTML report and:
1. Review CRITICAL findings (red)
2. Follow remediation recommendations
3. Use automated fixes where available

### Automate Scanning

```bash
# Create daily scan script
cat > daily_scan.sh << 'EOF'
#!/bin/bash
cd /path/to/cloud-security-toolkit
python cloud_security_audit.py \
  --provider aws \
  --format all \
  --output "scan_$(date +%Y%m%d)"
EOF

chmod +x daily_scan.sh

# Add to crontab (daily at 2 AM)
# crontab -e
# 0 2 * * * /path/to/daily_scan.sh
```

### Apply Automated Remediation

```bash
# Test first (dry-run)
python cloud_security_audit.py --remediate --dry-run

# Apply fixes (requires confirmation)
python cloud_security_audit.py --remediate

# Re-scan to verify improvements
python cloud_security_audit.py --output after_remediation.html
```

## Common Use Cases

### Compliance Audit
```bash
python cloud_security_audit.py \
  --provider aws \
  --format all \
  --output compliance_audit \
  --verbose
```

### Quick Security Check
```bash
python cloud_security_audit.py --provider aws --quiet
```

### Export for Reporting
```bash
python cloud_security_audit.py \
  --format csv \
  --output findings.csv
# Import into Excel/Jira/Confluence
```

## Troubleshooting

### "No credentials found"
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### "Permission denied"
Ensure your AWS IAM user has the `SecurityAudit` policy attached.

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Getting Help

- **Documentation**: See `docs/` directory
- **Installation Guide**: `docs/INSTALLATION.md`
- **Usage Guide**: `docs/USAGE.md`
- **Issues**: GitHub Issues

## Summary

You've now:
- ✅ Installed the toolkit
- ✅ Configured AWS credentials
- ✅ Run your first security scan
- ✅ Generated an HTML report
- ✅ Learned about automated remediation

**Next Steps**:
1. Review findings in the HTML report
2. Address CRITICAL and HIGH severity issues
3. Set up automated daily scans
4. Track your security score improvements

Happy securing! 🔒
