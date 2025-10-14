# Quick Command Reference

## 🚀 Quick Start

```bash
# 1. Run demo mode (no AWS needed)
python3 cloud_security_audit.py --demo --output demo_report.html
open demo_report.html

# 2. See what was generated
ls -lh demo_report.html
```

## 📊 All Report Formats

```bash
# Generate all formats at once
python3 cloud_security_audit.py --demo --format all --output my_audit

# Check reports/ directory
ls -lh reports/
```

## 🔍 Verification & Testing

```bash
# 1. Verify installation
python3 verify_installation.py

# 2. Check CLI help
python3 cloud_security_audit.py --help

# 3. Test demo mode
python3 demo_mode.py --output quick_test.html
```

## 🌐 With AWS Account

```bash
# 1. Configure credentials
aws configure

# 2. Test connectivity
aws sts get-caller-identity

# 3. Run real scan
python3 cloud_security_audit.py --provider aws --output aws_scan.html

# 4. All formats
python3 cloud_security_audit.py --provider aws --format all --output production_audit
```

## 🛠️ Remediation

```bash
# 1. Test fixes (safe - no changes)
python3 cloud_security_audit.py --provider aws --remediate --dry-run

# 2. Apply fixes (asks for confirmation)
python3 cloud_security_audit.py --provider aws --remediate

# 3. Re-scan to verify
python3 cloud_security_audit.py --provider aws --output after_fix.html
```

## 📋 Report Locations

```
reports/                              # All generated reports
demo_test_report.html                 # Demo HTML report
edge_case_test.json                   # Test JSON
/tmp/test_minimal.*                   # Test files
```

## 🎯 Common Use Cases

### Portfolio Demo
```bash
python3 cloud_security_audit.py --demo --format all --output portfolio_demo
```

### Daily Scan (Cron)
```bash
0 2 * * * cd /path/to/toolkit && python3 cloud_security_audit.py --provider aws --quiet --output "scan_$(date +\%Y\%m\%d).html"
```

### Compliance Audit
```bash
python3 cloud_security_audit.py --provider aws --format all --verbose --output compliance_audit
```

### Quick Security Check
```bash
python3 cloud_security_audit.py --provider aws --quiet
```

## 📝 File Locations

- Main CLI: `cloud_security_audit.py`
- Demo mode: `demo_mode.py`
- Verification: `verify_installation.py`
- Reports: `reports/` directory
- Documentation: `README.md`, `QUICKSTART.md`, `docs/`

## ✅ Status Check

Run this to verify everything works:
```bash
python3 verify_installation.py && \
python3 cloud_security_audit.py --demo --output status_check.html && \
echo "✅ All systems operational!"
```

---
Generated: October 14, 2025
Status: Production Ready ✅
